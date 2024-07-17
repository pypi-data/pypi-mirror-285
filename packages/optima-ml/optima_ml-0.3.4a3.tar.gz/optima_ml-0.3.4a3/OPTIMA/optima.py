"""Main steering script of OPTIMA."""

__author__ = "E. Bachmann"
__licence__ = "GPL3"
__version__ = "0.3.4alpha3"
__maintainer__ = "E. Bachmann"

import os
import sys
import shutil
import logging
import argparse
import threading
import functools

if sys.platform == "darwin":
    import multiprocess as mp
else:
    import multiprocessing as mp
import pickle
import time
import random as python_random

import numpy as np
import pyarrow
import optuna

# os.environ["TUNE_RESULT_BUFFER_LENGTH"] = "1000"  # buffer Tune results; allows for speculative execution of trials to reduce overhead during peak reporting
os.environ["RAY_DEDUP_LOGS"] = "0"  # disable log deduplication
# os.environ["TUNE_WARN_EXCESSIVE_EXPERIMENT_CHECKPOINT_SYNC_THRESHOLD_S"] = "0"  # temporary solution to disable annoying warnings until a better syncing is implemented
import ray
from ray import train, tune
from ray.tune.schedulers import ASHAScheduler, PopulationBasedTrainingReplay
# from ray.tune.search.hebo import HEBOSearch
from ray.tune.search.optuna import OptunaSearch
from ray.tune.logger import JsonLoggerCallback, CSVLoggerCallback
from optuna.samplers import TPESampler, RandomSampler

import OPTIMA.core.evaluation
import OPTIMA.core.inputs
import OPTIMA.core.search_space
import OPTIMA.core.tools
import OPTIMA.core.training
import OPTIMA.core.variable_optimization
import OPTIMA.builtin.inputs
import OPTIMA.builtin.model
import OPTIMA.builtin.search_space

import importlib.util
if importlib.util.find_spec("tensorflow") is not None:
    # suppress tensorflow info messages
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
    import OPTIMA.keras.training

if importlib.util.find_spec("lightning") is not None:
    # when using lightning, disable the UserWarning regarding the number of processes of the dataloader
    import warnings
    warnings.filterwarnings("ignore", ".*does not have many workers.*")
    import OPTIMA.lightning.inputs
    import OPTIMA.lightning.training

from OPTIMA.hardware_configs.helpers import get_cluster, get_suitable_job
from OPTIMA.resources.pbt_with_seed import PopulationBasedTraining


def setup_tensorflow(num_threads):
    # configure tensorflow to limit its thread usage and its memory usage if a gpu is used
    from tensorflow import config as tf_config
    try:
        # set automatic scaling of the VRAM allocation
        gpus = tf_config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf_config.experimental.set_memory_growth(gpu, True)

        # reduce number of threads
        tf_config.threading.set_inter_op_parallelism_threads(min(num_threads, 2))
        tf_config.threading.set_intra_op_parallelism_threads(num_threads)
    except RuntimeError:
        pass


def set_seeds(run_config, model_config):
    # fixed global random seeds (if provided) to make training deterministic
    if model_config.get("seed") is not None:
        if run_config.model_type == "Keras":
            import tensorflow as tf
            max_seeds = OPTIMA.core.tools.get_max_seeds()
            np.random.seed(model_config["seed"])
            python_random.seed(np.random.randint(*max_seeds))
            tf.keras.utils.set_random_seed(np.random.randint(*max_seeds))
            tf.random.set_seed(np.random.randint(*max_seeds))
        elif run_config.model_type == "Lightning":
            import lightning.pytorch as pl
            pl.seed_everything(model_config["seed"], workers=True)


def compile_metrics(run_config, native_metrics, weighted_native_metrics):
    # compile the metrics (needs to be done here (and not earlier) because tensorflow must not be initialized before setting inter- and intra-op threads)
    if run_config.model_type == "Keras":
        compiled_metrics = [metric(name=name, **metric_kwargs) for name, (metric, metric_kwargs) in
                            native_metrics]
        compiled_weighted_metrics = [metric(name=name, **metric_kwargs) for name, (metric, metric_kwargs) in
                                     weighted_native_metrics]
    elif run_config.model_type == "Lightning":
        compiled_metrics = [(f"{prefix}_{name}", metric(**metric_kwargs)) for name, (metric, metric_kwargs) in
                            native_metrics for prefix in ["train", "val"]]
        compiled_weighted_metrics = [(f"{prefix}_{name}", metric(**metric_kwargs)) for
                                     name, (metric, metric_kwargs) in
                                     weighted_native_metrics for prefix in ["train", "val"]]
    return compiled_metrics, compiled_weighted_metrics


def limit_hyperparameters(run_config, model_config):
    # limit all hyperparameters properly; since only non-conditional hyperparameters can go out of bounds (PBT does
    # not support conditional hps), we don't need to do any deserialization
    for hp, hp_search_space in run_config.search_space.items():
        if isinstance(hp_search_space, dict) and "bounds" in hp_search_space.keys() and hp in model_config.keys():
            bounds = hp_search_space["bounds"]
            if (isinstance(bounds[0], int) or isinstance(bounds[0], float)) and model_config[hp] < bounds[0]:
                model_config[hp] = bounds[0]
            elif (isinstance(bounds[1], int) or isinstance(bounds[1], float)) and model_config[hp] > bounds[1]:
                model_config[hp] = bounds[1]
    return model_config


def prepare_data(
    run_config,
    input_handler,
    model_config,
    inputs_train,
    targets_train,
    normalized_weights_train,
    inputs_val,
    targets_val,
    normalized_weights_val
):
    # convert the training, validation and testing data to tensorflow datasets or lightning dataloaders
    if run_config.model_type == "Keras":
        import tensorflow as tf
        train_data = tf.data.Dataset.from_tensor_slices((inputs_train, targets_train, normalized_weights_train))
        val_data = tf.data.Dataset.from_tensor_slices((inputs_val, targets_val, normalized_weights_val))

        # batch the datasets for tensorflow
        train_data = train_data.batch(model_config["batch_size"])
        val_data = val_data.batch(model_config["batch_size"])
        return train_data, val_data
    elif run_config.model_type == "Lightning":
        if hasattr(run_config, "DataModule"):
            DataModule = run_config.DataModule
        else:
            DataModule = OPTIMA.lightning.inputs.DefaultDataModule
        pl_data_module = DataModule(
            input_handler=input_handler,
            inputs_train=inputs_train,
            targets_train=targets_train,
            weights_train=normalized_weights_train,
            inputs_val=inputs_val,
            targets_val=targets_val,
            weights_val=normalized_weights_val,
            run_config=run_config,
            model_config=model_config
        )
        return pl_data_module


def update_model(run_config, model, model_config, input_handler, inputs_train, targets_train):
    if hasattr(run_config, 'update_model'):
        model = run_config.update_model(
            model,
            model_config,
            input_handler=input_handler,
            inputs_train=inputs_train,
            targets_train=targets_train,
        )
    else:
        model = OPTIMA.builtin.model.update_model(
            model,
            model_config,
            input_handler=input_handler,
            inputs_train=inputs_train,
            targets_train=targets_train,
        )
    return model

def reload_from_checkpoint(
    run_config,
    input_handler,
    model_config,
    early_stopper,
    inputs_train,
    targets_train,
    checkpoint_dir,
    restore_on_best_checkpoint
):
    if run_config.model_type == "Keras":
        import tensorflow as tf
        if not restore_on_best_checkpoint:
            model = tf.keras.models.load_model(os.path.join(checkpoint_dir, "model.keras"))  # reload the model
        else:
            model = tf.keras.models.load_model(
                os.path.join(checkpoint_dir, "best_model.keras"))  # reload the best model

        # since some hyperparameters may have been changed since the save, we need to update the model
        model = update_model(run_config, model, model_config, input_handler, inputs_train, targets_train)
    elif run_config.model_type == "Lightning":
        # update hyperparameters while loading checkpoint
        if not restore_on_best_checkpoint:
            model = run_config.LitModel.load_from_checkpoint(os.path.join(checkpoint_dir, "model.ckpt"),
                                                             model_config=model_config)
        else:
            model = run_config.LitModel.load_from_checkpoint(os.path.join(checkpoint_dir, "best_model.ckpt"),
                                                             model_config=model_config)

    # load current early stopper state, even when restoring on best model checkpoint
    early_stopper.load_state(checkpoint_dir)
    if run_config.model_type == "Keras":
        early_stopper.copy_best_model(os.path.join(checkpoint_dir, "best_model.keras"))
    elif run_config.model_type == "Lightning":
        early_stopper.copy_best_model(os.path.join(checkpoint_dir, "best_model.ckpt"))

    return model, early_stopper


def build_model(
    run_config,
    model_config,
    input_handler,
    inputs_train,
    targets_train,
    compiled_metrics,
    compiled_weighted_metrics
):
    if hasattr(run_config, 'build_model') and run_config.model_type == "Keras":
        model = run_config.build_model(
            model_config,
            input_handler=input_handler,
            inputs_train=inputs_train,
            targets_train=targets_train,
        )
    elif hasattr(run_config, 'LitModel') and run_config.model_type == "Lightning":
        model = run_config.LitModel(
            model_config,
            inputs_train.shape,
            targets_train.shape,
            compiled_metrics,
            compiled_weighted_metrics
        )
    else:
        if run_config.model_type == "Keras":
            model = OPTIMA.builtin.model.build_model(
                model_config,
                input_handler=input_handler,
                inputs_train=inputs_train,
                targets_train=targets_train,
            )
        elif run_config.model_type == "Lightning":
            raise NotImplementedError("Lightning models requires a LitModel-class to be present in the run-config.")
    return model


def compile_model(
    run_config,
    model,
    model_config,
    compiled_metrics,
    compiled_weighted_metrics,
    input_handler,
    inputs_train,
    targets_train,
    first_compile
):
    if run_config.model_type == "Keras":
        if hasattr(run_config, 'compile_model'):
            model = run_config.compile_model(
                model,
                model_config,
                metrics=compiled_metrics,
                weighted_metrics=compiled_weighted_metrics,
                input_handler=input_handler,
                inputs_train=inputs_train,
                targets_train=targets_train,
                first_compile=first_compile
            )
        else:
            model = OPTIMA.builtin.model.compile_model(
                model,
                model_config,
                metrics=compiled_metrics,
                weighted_metrics=compiled_weighted_metrics,
                input_handler=input_handler,
                inputs_train=inputs_train,
                targets_train=targets_train,
                first_compile=first_compile
            )
    elif run_config.model_type == "Lightning":
        model.prepare(input_handler, inputs_train, targets_train, first_prepare=first_compile)

    return model


def fit_model(run_config, model, early_stopper, data, end_epoch, num_threads, verbose):
    if run_config.model_type == "Keras":
        train_data, val_data = data
        model.fit(
            train_data,
            validation_data=val_data,
            epochs=end_epoch,
            initial_epoch=early_stopper.current_epoch,  # when continuing the training, set the correct epoch number
            callbacks=[early_stopper, *[c[0](**c[1]) for c in run_config.callbacks]],
            verbose=verbose
        )
        return model
    elif run_config.model_type == "Lightning":
        # set correct number of cpu cores; TODO: this for some reason currently only works with pytorch-gpu and is ignored by pytorch??
        from torch import get_num_threads, get_num_interop_threads, set_num_threads, set_num_interop_threads
        if get_num_threads() != num_threads:
            set_num_threads(num_threads)
        if get_num_interop_threads() != min(num_threads, 2):
            set_num_interop_threads(min(num_threads, 2))

        # currently, the device summary cannot be disabled. TODO: check if this has changed
        import lightning.pytorch as pl
        trainer = pl.Trainer(
            max_epochs=end_epoch,
            callbacks=[early_stopper, *[c[0](**c[1]) for c in run_config.callbacks]],
            devices='auto',
            accelerator='auto',
            num_sanity_val_steps=0,  # this messes with the reporting to Tune since it calls the Callbacks
            enable_progress_bar=False,
            enable_model_summary=False,
            logger=False,  # logging is done via Tune
            enable_checkpointing=False,  # checkpointing is done in the early stopper
        )
        trainer.fit_loop.epoch_progress.current.processed = early_stopper.current_epoch  # when continuing the training, set the correct epoch number
        trainer.fit(model, data)
        return model, trainer


def train_model(
    model_config,
    run_config,
    input_handler,
    inputs_train,
    inputs_val,
    targets_train,
    targets_val,
    normalized_weights_train,
    normalized_weights_val,
    monitor=('val_loss', 'min'),
    custom_metrics=[],
    composite_metrics=[],
    native_metrics=[],
    weighted_native_metrics=[],
    overtraining_conditions=[],
    early_stopping_patience=0,
    overtraining_patience=0,
    restore_best_weights=False,
    restore_on_best_checkpoint=False,
    num_threads=1,
    create_checkpoints=True,
    run_in_subprocess=True,
    verbose=2
):
    def _train_model(
        checkpoint_com,
        report_com,
        termination_event,
        start_time,
        model_config,
        run_config,
        input_handler,
        inputs_train,
        inputs_val,
        targets_train,
        targets_val,
        normalized_weights_train,
        normalized_weights_val,
        monitor,
        custom_metrics,
        composite_metrics,
        native_metrics,
        weighted_native_metrics,
        overtraining_conditions,
        early_stopping_patience,
        overtraining_patience,
        restore_best_weights,
        restore_on_best_checkpoint,
        num_threads,
        create_checkpoints,
        in_tune_session,
        runs_in_subprocess,
        verbose
    ):
        # setup the environment
        if run_config.model_type == "Keras":
            setup_tensorflow(num_threads)
            import tensorflow as tf
        elif run_config.model_type == "Lightning":
            import lightning.pytorch as pl

        # set the seeds
        set_seeds(run_config, model_config)

        # check if training data is given as ray.ObjectReference; if yes, get the objects from Ray's shared memory
        if isinstance(inputs_train, ray.ObjectRef):
            inputs_train, inputs_val, targets_train, targets_val, normalized_weights_train, normalized_weights_val = ray.get([
                inputs_train, inputs_val, targets_train, targets_val, normalized_weights_train, normalized_weights_val
            ])

        # get all events and queues for the inter-process communication:
        # - checkpoint_event and checkpoint_queue are used when checking if the trainable should reload from a checkpoint
        # - report_event and report_queue are used to report back results
        # - report_queue_read_event signifies that the main process has finished the report and the subprocess can continue training
        # - termination_event is set when the training terminates internally via EarlyStopping to tell the main process to return
        checkpoint_event, checkpoint_queue = checkpoint_com
        report_event, report_queue, report_queue_read_event = report_com

        # compile the metrics
        compiled_metrics, compiled_weighted_metrics = compile_metrics(run_config, native_metrics, weighted_native_metrics)

        # check if we have fixed hyperparameters or a hyperparameter schedule and build a list of hyperparameters in the
        # form [(start_epoch, end_epoch, model_config_iteration), ...] where the training should stop before end_epoch
        # when counting from start_epoch
        if "hp_schedule" in model_config:
            policy = model_config["hp_schedule"]
            hp_list = []
            for i, (start_epoch, model_config_iteration) in enumerate(policy):
                if i + 1 < len(policy):
                    end_epoch = policy[i+1][0]
                else:
                    end_epoch = model_config["max_epochs"]
                hp_list.append((start_epoch, end_epoch, model_config_iteration))
        else:
            hp_list = [(0, model_config["max_epochs"], model_config)]

        # save the early stopper state when performing hyperparameter schedule
        early_stopper_state = None

        # check if we need to reload from a checkpoint
        if in_tune_session:
            # check for Tune-managed checkpoint loading
            if runs_in_subprocess:
                # activate checkpoint event, then wait until queue is filled
                checkpoint_event.set()
                checkpoint = checkpoint_queue.get()
            else:
                # fetch checkpoint directly
                checkpoint = train.get_checkpoint()

            # convert checkpoint to directory path
            if checkpoint is not None:
                checkpoint = checkpoint.to_directory()
        elif "checkpoint_dir" in model_config.keys() and os.path.exists(model_config["checkpoint_dir"]) and \
                os.path.exists(os.path.join(model_config["checkpoint_dir"], "early_stopper")):
            # check for manual checkpoint
            checkpoint = model_config["checkpoint_dir"]
        else:
            checkpoint = None

        # iterate over hyperparameter list
        for hp_schedule_iteration, (start_epoch, end_epoch, model_config_iteration) in enumerate(hp_list):
            # limit all hyperparameters
            model_config_iteration = limit_hyperparameters(run_config, model_config_iteration)

            # convert the training and validation data to tensorflow datasets or lightning dataloaders
            data = prepare_data(
                run_config,
                input_handler,
                model_config_iteration,
                inputs_train,
                targets_train,
                normalized_weights_train,
                inputs_val,
                targets_val,
                normalized_weights_val
            )
            if run_config.model_type == "Keras":
                train_data, val_data = data
            elif run_config.model_type == "Lightning":
                pl_data_module = data

            # create the EarlyStopper instance
            if run_config.model_type == "Keras":
                early_stopper = OPTIMA.keras.training.EarlyStopperForKerasTuning(
                    monitor=monitor,
                    metrics=[metric_name for metric_name, _ in native_metrics],
                    weighted_metrics=[metric_name for metric_name, _ in weighted_native_metrics],
                    custom_metrics=custom_metrics,
                    composite_metrics=composite_metrics,
                    overfitting_conditions=overtraining_conditions,
                    patience_improvement=early_stopping_patience,
                    patience_overfitting=overtraining_patience,
                    inputs_train=train_data,
                    inputs_val=val_data,
                    targets_train=targets_train,
                    targets_val=targets_val,
                    weights_train=normalized_weights_train,
                    weights_val=normalized_weights_val,
                    restore_best_weights=restore_best_weights,
                    verbose=verbose,
                    create_checkpoints=create_checkpoints,
                    checkpoint_dir=model_config.get('checkpoint_dir'),
                    first_checkpoint_epoch=model_config["first_checkpoint_epoch"] if create_checkpoints else -1,
                    checkpoint_frequency=model_config["checkpoint_frequency"] if create_checkpoints else -1,
                    report_event=report_event,
                    report_queue=report_queue,
                    report_queue_read_event=report_queue_read_event,
                    termination_event=termination_event,
                    in_tune_session=in_tune_session
                )
            elif run_config.model_type == "Lightning":
                early_stopper = OPTIMA.lightning.training.EarlyStopperForLightningTuning(
                    run_config=run_config,
                    model_config=model_config_iteration,
                    monitor=monitor,
                    metrics=[metric_name for metric_name, _ in native_metrics],
                    weighted_metrics=[metric_name for metric_name, _ in weighted_native_metrics],
                    custom_metrics=custom_metrics,
                    composite_metrics=composite_metrics,
                    overfitting_conditions=overtraining_conditions,
                    patience_improvement=early_stopping_patience,
                    patience_overfitting=overtraining_patience,
                    inputs_train=inputs_train,
                    inputs_val=inputs_val,
                    targets_train=targets_train,
                    targets_val=targets_val,
                    weights_train=normalized_weights_train,
                    weights_val=normalized_weights_val,
                    restore_best_weights=restore_best_weights,
                    verbose=verbose,
                    create_checkpoints=create_checkpoints,
                    checkpoint_dir=model_config.get('checkpoint_dir'),
                    first_checkpoint_epoch=model_config["first_checkpoint_epoch"] if create_checkpoints else -1,
                    checkpoint_frequency=model_config["checkpoint_frequency"] if create_checkpoints else -1,
                    report_event=report_event,
                    report_queue=report_queue,
                    report_queue_read_event=report_queue_read_event,
                    termination_event=termination_event,
                    in_tune_session=in_tune_session
                )

            # apply the checkpoint if available
            if checkpoint is not None:
                # load the model and the early stopper state from the checkpoint
                model, early_stopper = reload_from_checkpoint(
                    run_config,
                    input_handler,
                    model_config_iteration,
                    early_stopper,
                    inputs_train,
                    targets_train,
                    checkpoint,
                    restore_on_best_checkpoint
                )
            elif hp_schedule_iteration > 0:
                # we are running a hyperparameter schedule, so we need to update the model and set the early stopper
                # state
                if run_config.model_type == "Keras":
                    model = update_model(
                        run_config,
                        model,
                        model_config_iteration,
                        input_handler,
                        inputs_train,
                        targets_train
                    )
                else:
                    # TODO: manually save and reload the model here?
                    raise NotImplementedError("Updating the hyperparameters of a Lightning model requires a checkpoint "
                                              "to load from, which could not be found!")
                early_stopper.set_state(early_stopper_state)
            else:
                # build model if it should not be reloaded from a checkpoint
                model = build_model(
                    run_config,
                    model_config_iteration,
                    input_handler,
                    inputs_train,
                    targets_train,
                    compiled_metrics,
                    compiled_weighted_metrics
                )

            # in any case, the model needs to be compiled / prepared (this is also necessary if only the regularizers have been updated!)
            model = compile_model(
                        run_config,
                        model,
                        model_config_iteration,
                        compiled_metrics,
                        compiled_weighted_metrics,
                        input_handler,
                        inputs_train,
                        targets_train,
                        first_compile=checkpoint is None and hp_schedule_iteration == 0
                    )

            if time.time() - start_time > 2 and hp_schedule_iteration == 0:
                logging.warning(f"Starting the subprocess and prepare training took {time.time()-start_time}s which may "
                                f"be a performance bottleneck.")

            # fit the model
            if run_config.model_type == "Keras":
                model = fit_model(run_config, model, early_stopper, (train_data, val_data), end_epoch, num_threads, verbose)
            elif run_config.model_type == "Lightning":
                model, trainer = fit_model(run_config, model, early_stopper, pl_data_module, end_epoch, num_threads, verbose)

            # save the early stopper state
            early_stopper_state = early_stopper.get_state()

        # if requested, save the final model
        if "final_model_path" in model_config.keys():
            if not os.path.exists(os.path.dirname(model_config["final_model_path"])):
                os.makedirs(os.path.dirname(model_config["final_model_path"]), exist_ok=True)
            if run_config.model_type == "Keras":
                out_path = model_config["final_model_path"] + ".keras"
                model.save(out_path, save_format="keras")
            elif run_config.model_type == "Lightning":
                out_path = model_config["final_model_path"] + ".ckpt"
                trainer.save_checkpoint(out_path)

        # tell the other process to stop waiting for reports and checkpoints and exit
        if runs_in_subprocess:
            termination_event.set()
            sys.exit(0)

    # check if we are in a tune session. If not, we don't need the reporting
    in_tune_session = train._internal.session.get_session() is not None

    # due to constantly increasing memory usage by tensorflow, the training can be executed in a separate process.
    # create all necessary events and queues for the inter-process communication (because air.session functions need to be
    # called from the main process!)
    if run_in_subprocess:
        checkpoint_event = mp.Event()
        checkpoint_queue = mp.Queue()
        report_event = mp.Event()
        report_queue = mp.Queue()
        report_queue_read_event = mp.Event()
        termination_event = mp.Event()

        # for some reason on Taurus, the subprocess may on some machines not be killed when the trial is terminated
        # (even though it is daemonic!). The only way I found to terminate the subprocess is to have a separate thread
        # listen for the threading event that Tune uses internally to signify itself that the trial should be terminated,
        # and kill the subprocess manually
        def _check_termination(end_event):
            """
            small helper function that waits until the end_event is set (which is done by Tune when the trial is terminated,
            e. g. by the scheduler) and then terminates the subprocess
            :return:
            """
            end_event.wait()
            p.kill()

        # check if we are in a tune session; if yes, start the watcher thread that terminates the subprocess once the trial
        # is terminated by the scheduler; if not, we don't need to do that as the main process will never be terminated
        # automatically
        if in_tune_session:
            end_event = train._internal.session.get_session().stop_event
            t = threading.Thread(target=_check_termination, args=(end_event,))
            t.start()

        # create and start the subprocess
        p = mp.Process(target=_train_model,
                       args=((checkpoint_event, checkpoint_queue),
                             (report_event, report_queue, report_queue_read_event),
                             termination_event,
                             time.time(),
                             model_config,
                             run_config,
                             input_handler,
                             inputs_train,
                             inputs_val,
                             targets_train,
                             targets_val,
                             normalized_weights_train,
                             normalized_weights_val,
                             monitor,
                             custom_metrics,
                             composite_metrics,
                             native_metrics,
                             weighted_native_metrics,
                             overtraining_conditions,
                             early_stopping_patience,
                             overtraining_patience,
                             restore_best_weights,
                             restore_on_best_checkpoint,
                             num_threads,
                             create_checkpoints,
                             in_tune_session,
                             run_in_subprocess,
                             verbose,
                             )
                       )
        p.daemon = True
        p.start()
    else:
        # directly call the training function
        _train_model(
            (None, None),
            (None, None, None),
            None,
            time.time(),
            model_config,
            run_config,
            input_handler,
            inputs_train,
            inputs_val,
            targets_train,
            targets_val,
            normalized_weights_train,
            normalized_weights_val,
            monitor,
            custom_metrics,
            composite_metrics,
            native_metrics,
            weighted_native_metrics,
            overtraining_conditions,
            early_stopping_patience,
            overtraining_patience,
            restore_best_weights,
            restore_on_best_checkpoint,
            num_threads,
            create_checkpoints,
            in_tune_session,
            run_in_subprocess,
            verbose,
        )

    # when running in subprocess: wait for events and fill / read from the queues when necessary + kill the subprocess in
    # the end
    if run_in_subprocess:
        while (not termination_event.is_set()) and p.is_alive():
            if in_tune_session:
                if checkpoint_event.is_set():
                    checkpoint_queue.put(train.get_checkpoint())
                    checkpoint_event.clear()
                if report_event.is_set():
                    epoch, results = report_queue.get()
                    if (create_checkpoints and epoch + 1 >= model_config["first_checkpoint_epoch"] and
                            (epoch + 1 - model_config["first_checkpoint_epoch"]) % model_config["checkpoint_frequency"] == 0):
                        checkpoint = train.Checkpoint.from_directory("checkpoint_dir")
                    time_before_report = time.time()
                    if (create_checkpoints and epoch + 1 >= model_config["first_checkpoint_epoch"] and
                            (epoch + 1 - model_config["first_checkpoint_epoch"]) % model_config["checkpoint_frequency"] == 0):
                        train.report(results, checkpoint=checkpoint)
                    else:
                        train.report(results)
                    report_event.clear()
                    report_queue_read_event.set()
                    if time.time() - time_before_report > 2:
                        logging.warning(
                            "Reporting results took {} seconds, which may be a performance bottleneck.".format(
                                time.time() - time_before_report))
            time.sleep(0.2)

        # make sure the subprocess is terminated before returning
        p.kill()


def do_optimization(args, run_config, defaults_config_str, cluster):
    # settings for the optimization
    resume_experiment = True  # if True, ray tune will resume an experiment if present at the location given by 'optimization_dir'; if no experiment is found, will start a new one
    optimize_name = ("best_" if run_config.optimize_on_best_value else "last_valid_") + run_config.monitor_name  # when run_config.optimize_on_best_value, the metric name given to ray needs to be different
    optimize_op = run_config.monitor_op
    target_metric_for_PBT_init = run_config.monitor_name  # when using multiple metrics for the optimization (not yet implemented, TODO!), need to specify one to select the fixed hyperparameters for PBT from the optuna results
    output_dir = OPTIMA.core.tools.get_output_dir(run_config)
    optimization_dir = os.path.join(output_dir, 'optimization')  # this is where all the optimization files are saved
    results_dir = os.path.join(output_dir, 'results')  # when the optimization is done, the best model for each method is copied here and evaluated

    # for later reproduction, copy the config to the output folder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    print("copying run-config from {} to {}".format(args.config, os.path.join(output_dir, "config.py")))
    try:
        shutil.copy2(args.config, os.path.join(output_dir, "config.py"))
    except shutil.SameFileError:
        print("Provided run-config is already in the output directory, skipping...")

    # also write the defaults config to the output folder
    if args.defaults is not None:
        print("copying defaults config from {} to {}".format(args.defaults, os.path.join(output_dir, "defaults.py")))
    else:
        print("copying built-in defaults config to {}".format(os.path.join(output_dir, "defaults.py")))
    with open(os.path.join(output_dir, "defaults.py"), "w") as f:
        f.write(defaults_config_str)

    # setting the resources for the optimization
    max_ram = int(args.cpus * args.mem_per_cpu * 1e6)  # convert to bytes which is what ray expects
    reservable_memory = int(0.75 * max_ram)  # leave a bit of ram free for the head
    object_store_memory = int(0.15 * max_ram)
    memory_per_trial = int(args.cpus_per_trial * args.mem_per_cpu * reservable_memory / max_ram * 1e6)
    print("Total available RAM in the cluster: " + str(max_ram / 1e9) + " GB")
    print("Reservable memory: " + str(reservable_memory / 1e9) + " GB")
    print("Object store memory: " + str(object_store_memory / 1e9) + " GB")
    print("Memory per trial: " + str(memory_per_trial / 1e9) + " GB")

    # when using the built-in build_model or compile_model-functions with Keras, get the corresponding hyperparameter
    # default values and update missing search space entries with the corresponding fixed defaults
    hyperparameter_defaults_build, hyperparameter_defaults_compile = OPTIMA.builtin.search_space.get_hp_defaults()
    if run_config.model_type == 'Keras' and not hasattr(run_config, 'build_model'):
        # check if 'units_i' hyperparameters are present in the search space. If yes, drop the 'units' default hyperparameter
        if any(["units" in hp for hp in run_config.search_space.keys()]):
            hyperparameter_defaults_build.pop("units")

        # add missing default values
        for hp_name, hp_value in hyperparameter_defaults_build.items():
            if hp_name not in run_config.search_space.keys():
                run_config.search_space[hp_name] = hp_value
    if run_config.model_type == 'Keras' and not hasattr(run_config, 'compile_model'):
        # add missing default values
        for hp_name, hp_value in hyperparameter_defaults_compile.items():
            if hp_name not in run_config.search_space.keys():
                run_config.search_space[hp_name] = hp_value

    # when using the built-in build_model or compile_model-functions with Keras, get the hyperparameters that allow
    # mutation, and mark their search space entries as such unless they are explicitly marked as non-mutatable in the
    # run-config
    mutatable_hps_build, mutatable_hps_compile = OPTIMA.builtin.search_space.get_hps_to_mutate()
    if run_config.model_type == 'Keras' and not hasattr(run_config, 'build_model'):
        for hp in mutatable_hps_build:
            if isinstance(run_config.search_space[hp], dict) and "supports_mutation" not in run_config.search_space[hp].keys():
                run_config.search_space[hp]["supports_mutation"] = True
    if run_config.model_type == 'Keras' and not hasattr(run_config, 'compile_model'):
        for hp in mutatable_hps_compile:
            if isinstance(run_config.search_space[hp], dict) and "supports_mutation" not in run_config.search_space[hp].keys():
                run_config.search_space[hp]["supports_mutation"] = True

    # add the maximum number of epochs and the first epoch to checkpoint and the checkpoint frequency to the search space.
    # Here, we want to start checkpointing after checkpoint_frequency epochs, so set first_checkpoint_epoch to
    # checkpoint_frequency
    run_config.search_space["max_epochs"] = run_config.max_epochs
    run_config.search_space["first_checkpoint_epoch"] = run_config.checkpoint_frequency
    run_config.search_space["checkpoint_frequency"] = run_config.checkpoint_frequency

    # build the search space for optuna
    search_space_optuna = functools.partial(
        OPTIMA.core.search_space.optuna_search_space,
        OPTIMA.core.search_space.serialize_conditions(run_config.search_space)
    )

    # setup ray
    if args.is_worker:
        ray.init(address=args.address, _temp_dir=cluster.ray_temp_path)
    else:
        ray.init(
            include_dashboard=False,
            num_cpus=args.cpus,
            num_gpus=args.gpus_per_worker,
            _memory=reservable_memory,
            object_store_memory=object_store_memory,
            _temp_dir=args.temp_dir
        )

    # get the input data; TODO: Ray datasets?
    if hasattr(run_config, 'InputHandler'):
        input_handler = run_config.InputHandler(run_config)
    else:
        input_handler = OPTIMA.builtin.inputs.InputHandler(run_config)
    if hasattr(run_config, 'get_experiment_inputs'):
        get_experiment_inputs = run_config.get_experiment_inputs
    else:
        get_experiment_inputs = OPTIMA.core.inputs.get_experiment_inputs
    inputs_split, targets_split, weights_split, normalized_weights_split = get_experiment_inputs(run_config,
                                                                                                                    input_handler,
                                                                                                                    output_dir=output_dir)

    if run_config.use_testing_dataset:
        inputs_train, inputs_val, inputs_test = inputs_split
        targets_train, targets_val, targets_test = targets_split
        weights_train, weights_val, weights_test = weights_split
        normalized_weights_train, normalized_weights_val, normalized_weights_test = normalized_weights_split
    else:
        inputs_train, inputs_val = inputs_split
        targets_train, targets_val = targets_split
        weights_train, weights_val = weights_split
        normalized_weights_train, normalized_weights_val = normalized_weights_split

    # get custom metrics
    custom_metrics = run_config.custom_metrics
    composite_metrics = run_config.composite_metrics
    native_metrics = run_config.native_metrics
    weighted_native_metrics = run_config.weighted_native_metrics

    # build the trainable
    trainable = OPTIMA.core.training.build_trainable(run_config, train_model, input_handler, inputs_train, inputs_val, targets_train,
                                                     targets_val, normalized_weights_train, normalized_weights_val,
                                                     num_threads=args.cpus_per_trial,
                                                     custom_metrics=custom_metrics,
                                                     composite_metrics=composite_metrics,
                                                     native_metrics=native_metrics,
                                                     weighted_native_metrics=weighted_native_metrics,
                                                     )

    # get the custom stopper that will terminate a trail when the custom early stopper said so
    stopper = OPTIMA.core.training.CustomStopper()

    # in case numpy is using int32 instead of int64, we can only have smaller values as seeds
    max_seeds = OPTIMA.core.tools.get_max_seeds()

    # initial optimization and input variable optimization
    if run_config.perform_variable_opt:
        print("Starting initial optimization phase using Optuna with ASHA scheduler...")
        print("Search space:")
        print(run_config.search_space)

        # to make Optimization reproducible (within the limits of high parallelization), set the random seeds
        if run_config.random_seed is not None:
            random_seed = run_config.random_seed
        else:
            random_seed = np.random.randint(*max_seeds)
        print(f"Using random seed: {random_seed}")
        rng_varOpt = np.random.RandomState(random_seed)

        # create the directories
        if run_config.perform_main_hyperopt or run_config.perform_PBT_hyperopt:
            optimization_dir_varOpt = os.path.join(optimization_dir, "variable_optimization")
            results_dir_variableOpt = os.path.join(results_dir, "variable_optimization")
        else:
            optimization_dir_varOpt = optimization_dir
            results_dir_variableOpt = results_dir
        if not os.path.exists(optimization_dir_varOpt):
            os.makedirs(optimization_dir_varOpt, exist_ok=True)
        if not os.path.exists(results_dir_variableOpt):
            os.makedirs(results_dir_variableOpt, exist_ok=True)

        if not os.path.isfile(os.path.join(results_dir_variableOpt, "analysis.pickle")):
            # the only way to add a unique random seed for each trial is to include it as part of the hyperparameter
            # suggestions. Since we don't want the search algorithm to try to optimize the seed, we cannot include it in
            # the search space (i.e. via a uniform distribution). Instead, create a subclass of the searcher that adds a
            # randomly generated seed to the suggestions, thus the searcher does not know about the seed at all.
            OptunaWithSeed = OPTIMA.core.search_space.add_random_seed_suggestions(rng_varOpt.randint(*max_seeds))(OptunaSearch)
            if run_config.use_TPESampler:
                sampler = TPESampler(
                    multivariate=run_config.use_multivariate_TPE,
                    warn_independent_sampling=True,
                    n_startup_trials=max(args.max_pending_trials, 10),
                    seed=rng_varOpt.randint(*max_seeds)
                )
            else:
                sampler = RandomSampler(
                    seed=rng_varOpt.randint(*max_seeds)
                )
            search_algo = OptunaWithSeed(
                metric=optimize_name,
                mode=optimize_op,
                sampler=sampler,
                space=search_space_optuna,
            )

            asha_scheduler = ASHAScheduler(
                grace_period=run_config.ASHA_grace_period,
                max_t=run_config.ASHA_max_t,
                reduction_factor=run_config.ASHA_reduction_factor,
                stop_last_trials=False
            ) if run_config.use_ASHAScheduler else None

            resume_failed = False
            if resume_experiment and tune.Tuner.can_restore(os.path.abspath(optimization_dir_varOpt)):
                # currently, restore does not handle relative paths; TODO: still True?
                tuner = tune.Tuner.restore(os.path.abspath(optimization_dir_varOpt), trainable=trainable, resume_errored=True)
            else:
                tuner = tune.Tuner(
                    tune.with_resources(
                        trainable,
                        resources=tune.PlacementGroupFactory([{"CPU": args.cpus_per_trial, "GPU": args.gpus_per_trial, "memory": memory_per_trial}]),
                    ),
                    # param_space=search_space,
                    run_config=train.RunConfig(
                        name=os.path.basename(optimization_dir_varOpt),
                        storage_path=os.path.dirname(os.path.abspath(optimization_dir_varOpt)),  # with Ray 2.7 this needs to be absolute, otherwise Ray complains about write permissions?
                        stop=stopper,
                        checkpoint_config=train.CheckpointConfig(
                            num_to_keep=1,
                            # checkpoint_score_attribute=optimize_name,
                            # checkpoint_score_order=optimize_op
                        ),
                        failure_config=train.FailureConfig(
                            max_failures=-1,
                        ),
                        callbacks=[JsonLoggerCallback(), CSVLoggerCallback()],
                        verbose=1,
                    ),
                    tune_config=tune.TuneConfig(
                        search_alg=search_algo,
                        scheduler=asha_scheduler,
                        metric=optimize_name,
                        mode=optimize_op,
                        num_samples=run_config.num_samples_variableOpt,
                        reuse_actors=True,
                    ),
                )

            results_grid = tuner.fit()
            analysis = results_grid._experiment_analysis

            # fetch the optuna study, transfer everything to a new study (whose storage is not in memory) and save it to file
            optuna_study = search_algo._ot_study
            if optuna_study is not None:
                new_optuna_study = optuna.create_study(
                    study_name="optuna_study_preOpt",
                    storage=f"sqlite:///{os.path.join(results_dir_variableOpt, 'optuna_study.db')}",
                    sampler=optuna_study.sampler,
                    pruner=optuna_study.pruner
                )
                new_optuna_study.add_trials(optuna_study.trials)
            else:
                logging.warning("Could not fetch Optuna study, was the optimization reloaded? Skipping...")

            # check if the experiment finished or was aborted (e.g. by KeyboardInterrupt)
            success_str = "\nInitial optimization run finished!"
            failure_str = "Experiment did not finish. This indicates that either an error occured or the execution was interrupted " \
                          "(e. g. via KeyboardInterrupt). Skipping variable and hyperparameter optimization. Exiting..."
            OPTIMA.core.tools.check_optimization_finished(results_grid, run_config.num_samples_variableOpt, success_str, failure_str)

            # save the analysis file to disk
            with open(os.path.join(results_dir_variableOpt, "analysis.pickle"), "wb") as file:
                pickle.dump(analysis, file)
        else:
            print("Finished experiment found, reloading the analysis.pickle file...")
            with open(os.path.join(results_dir_variableOpt, "analysis.pickle"), "rb") as file:
                analysis = pickle.load(file)

        # evaluate optimization results
        best_trials, best_trials_fit, configs_df, results_str, crossval_model_info, crossval_input_data = \
            OPTIMA.core.evaluation.evaluate_experiment(analysis,
                                                       train_model,
                                                       run_config,
                                                       run_config.monitor_name,
                                                       run_config.monitor_op,
                                                       run_config.search_space,
                                                       results_dir_variableOpt,
                                                       inputs_split,
                                                       targets_split,
                                                       weights_split,
                                                       normalized_weights_split,
                                                       input_handler,
                                                       custom_metrics=custom_metrics,
                                                       composite_metrics=composite_metrics,
                                                       native_metrics=native_metrics,
                                                       weighted_native_metrics=weighted_native_metrics,
                                                       cpus_per_model=args.cpus_per_trial,
                                                       gpus_per_model=args.gpus_per_trial,
                                                       overtraining_conditions=run_config.overtraining_conditions,
                                                       write_results=False,
                                                       return_results_str=True,
                                                       return_crossval_models=True,
                                                       seed=rng_varOpt.randint(*max_seeds))

        # check if variable optimization has been done before (because experiment was paused and resumed)
        if not os.path.exists(os.path.join(results_dir_variableOpt, "optimized_vars.pickle")):
            # get the paths of the crossvalidation models
            models = []
            best_value_model_config = None
            selection_string = "best_fit" if run_config.use_fit_results_for_varOpt else "best_value"
            for directory in crossval_model_info.keys():
                if selection_string in directory:
                    for model_info in crossval_model_info[directory]:
                        models.append((os.path.join(directory, model_info["name"]), crossval_input_data[model_info["split"]]))
                        if best_value_model_config is None: best_value_model_config = model_info["config"]

            # perform the variable optimization to get an optimized set of input variables and update run_config.input_vars accordingly
            print("Performing input variable optimization...")
            run_config.input_vars = OPTIMA.core.variable_optimization.perform_variable_optimization(models, best_value_model_config,
                                                                                                    run_config, input_handler, train_model,
                                                                                                    target_metric=run_config.var_metric,
                                                                                                    metric_op=run_config.var_metric_op,
                                                                                                    custom_metrics=custom_metrics,
                                                                                                    composite_metrics=composite_metrics,
                                                                                                    native_metrics=native_metrics,
                                                                                                    weighted_native_metrics=weighted_native_metrics,
                                                                                                    results_folder=results_dir_variableOpt,
                                                                                                    plots_folder=os.path.join(results_dir_variableOpt,
                                                                                                              "variable_opt_plots"),
                                                                                                    cpus_per_model=args.cpus_per_trial,
                                                                                                    gpus_per_model=args.gpus_per_trial,
                                                                                                    mode=run_config.variable_optimization_mode,
                                                                                                    seed=rng_varOpt.randint(*max_seeds))

            # dump the optimized variable list to file
            with open(os.path.join(results_dir_variableOpt, "optimized_vars.pickle"), 'wb') as optimized_vars_file:
                pickle.dump(run_config.input_vars, optimized_vars_file)

            # cleanup
            del models
        else:
            # if variable optimization was done before, just reload the optimized variable list
            print("Reloading previous input variable optimization...")
            with open(os.path.join(results_dir_variableOpt, "optimized_vars.pickle"), 'rb') as optimized_vars_file:
                run_config.input_vars = pickle.load(optimized_vars_file)

        # once done, delete crossval_input_data to clear the objects from the object store
        del crossval_input_data

        # print results
        print("Optimized input variables: {}".format(", ".join(run_config.input_vars)))
        print("variables dropped: {}".format(", ".join([var for var in input_handler.get_vars() if var not in run_config.input_vars])))

        # write results to file
        results_str += "\n\ninput variables after optimization: {}\n".format(", ".join(run_config.input_vars))
        results_str += "variables dropped: {}".format(", ".join([var for var in input_handler.get_vars() if var not in run_config.input_vars]))
        with open(os.path.join(results_dir_variableOpt, "results.txt"), 'w') as results_file:
            results_file.write(results_str)

        # reload the training data for the optimized input variables
        print("Reloading the training data...")
        input_handler.set_vars(run_config.input_vars)
        if hasattr(run_config, 'get_experiment_inputs'):
            inputs_split, targets_split, weights_split, normalized_weights_split = run_config.get_experiment_inputs(
                run_config, input_handler, output_dir=output_dir)
        else:
            inputs_split, targets_split, weights_split, normalized_weights_split = OPTIMA.core.inputs.get_experiment_inputs(
                run_config,
                input_handler,
                output_dir=output_dir)
        if run_config.use_testing_dataset:
            inputs_train, inputs_val, inputs_test = inputs_split
            targets_train, targets_val, targets_test = targets_split
            weights_train, weights_val, weights_test = weights_split
            normalized_weights_train, normalized_weights_val, normalized_weights_test = normalized_weights_split
        else:
            inputs_train, inputs_val = inputs_split
            targets_train, targets_val = targets_split
            weights_train, weights_val = weights_split
            normalized_weights_train, normalized_weights_val = normalized_weights_split

        # rebuild the trainable
        trainable = OPTIMA.core.training.build_trainable(run_config, train_model, input_handler, inputs_train, inputs_val, targets_train,
                                                         targets_val, normalized_weights_train, normalized_weights_val,
                                                         num_threads=args.cpus_per_trial,
                                                         custom_metrics=custom_metrics,
                                                         composite_metrics=composite_metrics,
                                                         native_metrics=native_metrics,
                                                         weighted_native_metrics=weighted_native_metrics
                                                         )

    # hyperparameter optimization with Optuna and ASHA
    if run_config.perform_main_hyperopt:
        print("Starting hyperparameter optimization using Optuna with ASHA scheduler...")
        print("Search space:")
        print(run_config.search_space)

        # to make Optimization reproducible (within the limits of high parallelization), set the random seeds
        if run_config.random_seed is not None:
            random_seed = run_config.random_seed
        else:
            random_seed = np.random.randint(*max_seeds)
        print(f"Using random seed: {random_seed}")
        random_seed = (random_seed * 2) % max_seeds[1]
        rng_optuna = np.random.RandomState(random_seed)

        # if a variable optimization was performed before or PBT is performed after the Optuna+ASHA run, add subdirectory to optimization_dir
        if run_config.perform_variable_opt or run_config.perform_PBT_hyperopt:
            optimization_dir_optuna = os.path.join(optimization_dir, "optuna+ASHA")
            results_dir_optuna = os.path.join(results_dir, "optuna+ASHA")
        else:
            optimization_dir_optuna = optimization_dir
            results_dir_optuna = results_dir
        if not os.path.exists(optimization_dir_optuna):
            os.makedirs(optimization_dir_optuna, exist_ok=True)
        if not os.path.exists(results_dir_optuna):
            os.makedirs(results_dir_optuna, exist_ok=True)

        if not os.path.isfile(os.path.join(results_dir_optuna, "analysis.pickle")):
            # the only way to add a unique random seed for each trial is to include it as part of the hyperparameter
            # suggestions. Since we don't want the search algorithm to try to optimize the seed, we cannot include it in
            # the search space (i.e. via a uniform distribution). Instead, create a subclass of the searcher that adds a
            # randomly generated seed to the suggestions, thus the searcher does not know about the seed at all.
            OptunaWithSeed = OPTIMA.core.search_space.add_random_seed_suggestions(rng_optuna.randint(*max_seeds))(OptunaSearch)
            if run_config.use_TPESampler:
                sampler = TPESampler(
                    multivariate=run_config.use_multivariate_TPE,
                    warn_independent_sampling=True,
                    n_startup_trials=max(args.max_pending_trials, 10),
                    seed=rng_optuna.randint(*max_seeds)
                )
            else:
                sampler = RandomSampler(
                    seed=rng_optuna.randint(*max_seeds)
                )
            search_algo = OptunaWithSeed(
                metric=optimize_name,
                mode=optimize_op,
                sampler=sampler,
                space=search_space_optuna,
            )

            asha_scheduler = ASHAScheduler(
                grace_period=run_config.ASHA_grace_period,
                max_t=run_config.ASHA_max_t,
                reduction_factor=run_config.ASHA_reduction_factor,
                stop_last_trials=False
            ) if run_config.use_ASHAScheduler else None

            if resume_experiment and tune.Tuner.can_restore(os.path.abspath(optimization_dir_optuna)):
                # currently, restore does not handle relative paths; TODO: still True?
                tuner = tune.Tuner.restore(os.path.abspath(optimization_dir_optuna), trainable=trainable, resume_errored=True)
            else:
                tuner = tune.Tuner(
                    tune.with_resources(
                        trainable,
                        resources=tune.PlacementGroupFactory(
                            [{"CPU": args.cpus_per_trial, "GPU": args.gpus_per_trial, "memory": memory_per_trial}]),
                    ),
                    # param_space=search_space,
                    run_config=train.RunConfig(
                        name=os.path.basename(optimization_dir_optuna),
                        storage_path=os.path.dirname(os.path.abspath(optimization_dir_optuna)),  # with Ray 2.7 this needs to be absolute, otherwise Ray complains about write permissions?
                        stop=stopper,
                        checkpoint_config=train.CheckpointConfig(
                            num_to_keep=1,
                            # checkpoint_score_attribute=optimize_name,
                            # checkpoint_score_order=optimize_op
                        ),
                        failure_config=train.FailureConfig(
                            max_failures=-1,
                        ),
                        # callbacks=[JsonLoggerCallback(), CSVLoggerCallback()],
                        verbose=1,
                    ),
                    tune_config=tune.TuneConfig(
                        search_alg=search_algo,
                        scheduler=asha_scheduler,
                        metric=optimize_name,
                        mode=optimize_op,
                        num_samples=run_config.num_samples_main,
                        reuse_actors=True,
                    ),
                )

            results_grid = tuner.fit()
            analysis = results_grid._experiment_analysis

            # fetch the optuna study, transfer everything to a new study (whose storage is not in memory) and save it to file
            optuna_study = search_algo._ot_study
            if optuna_study is not None:
                new_optuna_study = optuna.create_study(
                    study_name="optuna_study_main",
                    storage=f"sqlite:///{os.path.join(results_dir_optuna, 'optuna_study.db')}",
                    sampler=optuna_study.sampler,
                    pruner=optuna_study.pruner
                )
                new_optuna_study.add_trials(optuna_study.trials)
            else:
                logging.warning("Could not fetch Optuna study, was the optimization reloaded? Skipping...")

            # check if the experiment finished or was aborted (e.g. by KeyboardInterrupt)
            success_str = "\nOptuna+ASHA run finished!"
            failure_str = "Experiment did not finish. This indicates that either an error occured or the execution was interrupted " \
                          "(e. g. via KeyboardInterrupt). Skipping evaluation" + (" and PBT run." if run_config.perform_PBT_hyperopt else ".") \
                          + " Exiting..."
            OPTIMA.core.tools.check_optimization_finished(results_grid, run_config.num_samples_main, success_str, failure_str)

            # save the analysis file to disk
            with open(os.path.join(results_dir_optuna, "analysis.pickle"), "wb") as file:
                pickle.dump(analysis, file)
        else:
            print("Finished experiment found, reloading the analysis.pickle file...")
            with open(os.path.join(results_dir_optuna, "analysis.pickle"), "rb") as file:
                analysis = pickle.load(file)

        # evaluate optimization results
        best_trials, best_trials_fit, configs_df = \
            OPTIMA.core.evaluation.evaluate_experiment(analysis,
                                                       train_model,
                                                       run_config,
                                                       run_config.monitor_name,
                                                       run_config.monitor_op,
                                                       run_config.search_space,
                                                       results_dir_optuna,
                                                       inputs_split,
                                                       targets_split,
                                                       weights_split,
                                                       normalized_weights_split,
                                                       input_handler,
                                                       custom_metrics=custom_metrics,
                                                       composite_metrics=composite_metrics,
                                                       native_metrics=native_metrics,
                                                       weighted_native_metrics=weighted_native_metrics,
                                                       cpus_per_model=args.cpus_per_trial,
                                                       gpus_per_model=args.gpus_per_trial,
                                                       overtraining_conditions=run_config.overtraining_conditions,
                                                       seed=rng_optuna.randint(*max_seeds))

    if run_config.perform_PBT_hyperopt:
        print("Starting hyperparameter optimization using Population Based Training...")

        # to make Optimization reproducible (within the limits of high parallelization), set the random seeds
        if run_config.random_seed is not None:
            random_seed = run_config.random_seed
        else:
            random_seed = np.random.randint(*max_seeds)
        print(f"Using random seed: {random_seed}")
        random_seed = (random_seed * 3) % max_seeds[1]
        rng_PBT = np.random.RandomState(random_seed)

        # for PBT, set all non-mutatable hyperparameters to the fixed best values found during the main hyperparameter
        # optimization
        if run_config.perform_variable_opt or run_config.perform_main_hyperopt:
            print("Grabbing the best parameters from the Optuna+ASHA run to update the config...")
            best_hp_values_optuna = {
                hp: values for hp, values in zip(
                    configs_df.index,
                    configs_df[target_metric_for_PBT_init + (" fit" if run_config.use_fit_results_for_PBT else "")]
                )
            }
        else:
            best_hp_values_optuna = None

        # prepare the search space for PBT and get the mutatable subset of the search space
        search_space_PBT, hyperparams_to_mutate = OPTIMA.core.search_space.prepare_search_space_for_PBT(run_config.search_space, best_hp_values_optuna)

        # for PBT, we need a checkpoint on the last epoch of each perturbation interval. If the burn-in period and the
        # perturbation interval are both divisible by the checkpointing frequency, this works out. If the burn-in period
        # is not divisible by the checkpointing frequency, set the first checkpoint to be at the end of the burn-in
        # period. If the perturbation interval is not divisible by the checkpointing frequency, set the checkpointing
        # frequency to the perturbation interval.
        if run_config.burn_in_period % run_config.checkpoint_frequency != 0:
            print(f"The PBT burn-in period of {run_config.burn_in_period} epochs is not divisible by the checkpointing "
                  f"frequency of {run_config.checkpoint_frequency} epochs. Creating the first checkpoint after "
                  f"{run_config.burn_in_period} epochs.")
            search_space_PBT["first_checkpoint_epoch"] = run_config.burn_in_period
        if run_config.perturbation_interval % run_config.checkpoint_frequency != 0:
            print(f"The PBT perturbation interval of {run_config.perturbation_interval} epochs is not divisible by the "
                  f"checkpointing frequency of {run_config.checkpoint_frequency} epochs. Setting the checkpointing "
                  f"frequency to {run_config.perturbation_interval} epochs.")
            search_space_PBT["checkpoint_frequency"] = run_config.perturbation_interval

        # print the updated search space
        print("Updated search space:")
        print(search_space_PBT)

        # Print the hyperparameters to mutate
        print("Hyperparameters to mutate:")
        print(hyperparams_to_mutate)

        # since the search algorithm is completely ignored when using PBT, we cannot do the same trick to include the
        # random seed as for Optuna. Fortunately, PBT only optimizes hyperparameters provided in hyperparams_to_mutate,
        # so we can simply add a new search space entry for the seed. Unfortunately, the only way to make the sampling
        # from Tune search space entries reproducible is to set the numpy global random state.
        np.random.seed(rng_PBT.randint(*max_seeds))
        search_space_PBT["seed"] = tune.randint(*max_seeds)

        # if variable optimization or Optuna+ASHA run was performed before PBT, add subdirectory to optimization_dir
        if run_config.perform_variable_opt or run_config.perform_main_hyperopt:
            optimization_dir_PBT = os.path.join(optimization_dir, "PBT")
            results_dir_PBT = os.path.join(results_dir, "PBT")
        else:
            optimization_dir_PBT = optimization_dir
            results_dir_PBT = results_dir
        if not os.path.exists(optimization_dir_PBT):
            os.makedirs(optimization_dir_PBT, exist_ok=True)
        if not os.path.exists(results_dir_PBT):
            os.makedirs(results_dir_PBT, exist_ok=True)

        # since PBT only uses the RandomSampler, we can safely increase the number of pending trails
        os.environ['TUNE_MAX_PENDING_TRIALS_PG'] = str(run_config.num_samples_PBT)

        if not os.path.isfile(os.path.join(results_dir_PBT, "analysis.pickle")):
            if resume_experiment and tune.Tuner.can_restore(os.path.abspath(optimization_dir_PBT)):
                # currently, restore does not handle relative paths; TODO: still true?
                tuner = tune.Tuner.restore(os.path.abspath(optimization_dir_PBT), trainable=trainable, resume_errored=True)
            else:
                # configure population based training
                pbt = PopulationBasedTraining(
                    time_attr="training_iteration",
                    perturbation_interval=run_config.perturbation_interval,
                    burn_in_period=run_config.burn_in_period,
                    hyperparam_mutations=hyperparams_to_mutate,
                    seed=rng_PBT.randint(*max_seeds)
                )

                # get the Tuner
                tuner = tune.Tuner(
                    tune.with_resources(
                        trainable,
                        resources=tune.PlacementGroupFactory(
                            [{"CPU": args.cpus_per_trial, "GPU": args.gpus_per_trial, "memory": memory_per_trial}]),
                        # resources={"cpu": cpus_per_trial, "gpu": args.gpus_per_trial, "memory": memory_per_trial},
                    ),
                    param_space=search_space_PBT,
                    run_config=train.RunConfig(
                        name=os.path.basename(optimization_dir_PBT),
                        storage_path=os.path.abspath(os.path.dirname(optimization_dir_PBT)),
                        # with Ray 2.7 this needs to be absolute, otherwise Ray complains about write permissions?
                        stop=stopper,
                        checkpoint_config=train.CheckpointConfig(
                            num_to_keep=None,
                            # checkpoint_score_attribute=optimize_name,
                            # checkpoint_score_order=optimize_op
                        ),
                        failure_config=train.FailureConfig(
                            max_failures=-1,
                        ),
                        # callbacks=[JsonLoggerCallback(), CSVLoggerCallback()],
                        verbose=1,
                    ),
                    tune_config=tune.TuneConfig(
                        # search_alg=BasicVariantGenerator(random_state=rng_PBT.randint(*max_seeds)) if not replay else None,
                        scheduler=pbt,
                        metric=optimize_name,
                        mode=optimize_op,
                        num_samples=run_config.num_samples_PBT,
                        reuse_actors=True,
                    ),
                )

            results_grid = tuner.fit()
            analysis = results_grid._experiment_analysis

            # check if the experiment finished or was aborted (e.g. by KeyboardInterrupt)
            success_str = "\nPBT run finished!"
            failure_str = "Experiment did not finish. This indicates that either an error occured or the execution was interrupted " \
                          "(e. g. via KeyboardInterrupt). Skipping evaluation. Exiting..."
            OPTIMA.core.tools.check_optimization_finished(results_grid, run_config.num_samples_PBT, success_str, failure_str)

            # save the analysis file to disk
            with open(os.path.join(results_dir_PBT, "analysis.pickle"), "wb") as file:
                pickle.dump(analysis, file)
        else:
            print("Finished experiment found, reloading the analysis.pickle file...")
            with open(os.path.join(results_dir_PBT, "analysis.pickle"), "rb") as file:
                analysis = pickle.load(file)

        # prepare the mutation handler
        if os.path.exists(os.path.join(results_dir_PBT, "PBT_mutation_policies.pickle")):
            # load from the save state
            pbt_mutation_handler = OPTIMA.core.training.PBTMutationHandler()
            pbt_mutation_handler.load(os.path.join(results_dir_PBT, "PBT_mutation_policies.pickle"))
        else:
            # prepare the PBT mutation handler and load from the experiment state
            pbt_mutation_handler = OPTIMA.core.training.PBTMutationHandler()
            pbt_mutation_handler.load_experiment_state(optimization_dir_PBT)

            # save the mutation policies to the results directory
            pbt_mutation_handler.save(os.path.join(results_dir_PBT, "PBT_mutation_policies.pickle"))

        # evaluate optimization results
        best_trials, best_trials_fit, configs_df = \
            OPTIMA.core.evaluation.evaluate_experiment(analysis,
                                                       train_model,
                                                       run_config,
                                                       run_config.monitor_name,
                                                       run_config.monitor_op,
                                                       search_space_PBT,
                                                       results_dir_PBT,
                                                       inputs_split,
                                                       targets_split,
                                                       weights_split,
                                                       normalized_weights_split,
                                                       input_handler,
                                                       custom_metrics=custom_metrics,
                                                       composite_metrics=composite_metrics,
                                                       native_metrics=native_metrics,
                                                       weighted_native_metrics=weighted_native_metrics,
                                                       cpus_per_model=args.cpus_per_trial,
                                                       gpus_per_model=args.gpus_per_trial,
                                                       overtraining_conditions=run_config.overtraining_conditions,
                                                       PBT=True,
                                                       PBT_mutation_handler=pbt_mutation_handler,
                                                       seed=rng_PBT.randint(*max_seeds))

def initialize(args, run_config, cluster, custom_cluster_config=None):
    # get the cluster and configure the job
    if custom_cluster_config is not None and hasattr(custom_cluster_config, "ClusterJob"):
        job = custom_cluster_config.ClusterJob
    else:
        job = get_suitable_job(cluster)
    job.name = args.name
    job.log_path_out = f"logs/sbatch_{args.name}.olog"
    job.log_path_error = f"logs/sbatch_{args.name}.elog"
    job.runtime = args.runtime
    job.mem_per_cpu = args.mem_per_cpu
    job.use_SMT = False

    if args.fixed_ray_node_size:
        job.nodes = args.workers
        job.tasks_per_node = 1
        job.cpus_per_task = args.cpus_per_worker
        job.gpus_per_node = args.gpus_per_worker
    else:
        job.tasks = int(args.cpus / args.min_cpus_per_ray_node)
        job.cpus_per_task = args.min_cpus_per_ray_node

    # get the port config for the cluster
    port_config = cluster.get_ports()

    # if args.exclude_head_nodes, get the list of machines that already run head nodes and pass it to the ClusterJob,
    # also add nodes that should be excluded (given by the user via args.exclude)
    if args.exclude_head_nodes or args.exclude != "":
        # get all running head nodes and explicitly exclude them
        with open(cluster.ray_headnodes_path, "rb") as head_nodes_file:
            head_nodes = pickle.load(head_nodes_file)

        exclude_node_list = []
        for _, node, _ in head_nodes:
            exclude_node_list.append(node)
        exclude_node_list += args.exclude.split(",")
        job.excludes_list = exclude_node_list
    else:
        job.excludes_list = []

    def _optional_argument_formatter(key, value):
        if value is not None and value != "":
            if isinstance(value, bool) and value:  # prevent integer 1 and 0 from being interpreted as bools
                return f"--{key} "
            if isinstance(value, bool) and not value:
                return ""
            else:
                return f"--{key} {value} "
        else:
            return ""

    # setup the environment
    environment_str = """source {}""".format(run_config.path_to_setup_file)

    # when running many trials on the same worker, the default user limit for the max. number of processes of 4096 is not
    # sufficient. Increasing it allows more parallel trials.
    ulimit_str = """

# increase user processes limit
ulimit -u 100000""" if args.apply_ulimit_fix else ""

    ray_setup_str_1 = f"""# Getting the node names for this job
echo nodes for this job: {cluster.get_job_nodes_list_bash()}

# getting the paths to the executables
OPTIMA_PATH={'$(which optima)' if not args.local_source else './OPTIMA-runner.py'}
MANAGE_NODES_PATH={'$(which manage_ray_nodes)' if not args.local_source else './node-manager-runner.py'}
if [ -z $OPTIMA_PATH ]; then OPTIMA_PATH=./OPTIMA-runner.py; fi
if [ -z $MANAGE_NODES_PATH ]; then MANAGE_NODES_PATH=./node-manager-runner.py; fi

# run manage_ray_nodes to check which nodes are not yet running a ray head node and to get a sorted list of nodes for this job
# and an instance_num that is used to assign unique ports for the communication.
$MANAGE_NODES_PATH --cluster {args.cluster} \
--sorted_nodes_path temp_sorted_nodes_{cluster.get_job_id_bash()}.txt \
--sorted_cpus_per_node_path temp_sorted_cpus_per_node_{cluster.get_job_id_bash()}.txt \
--instance_num_path temp_instance_num_{cluster.get_job_id_bash()}.txt
EXIT_CODE=$?

# exit code of manage_ray_nodes is 0 if everything went fine and 129 if no free node was found. Anything else
# indicates an error, e.g. the file containing the running head nodes is not writable.
if [ $EXIT_CODE == 129 ]; then
    # If all nodes are running a head node already, execute OPTIMA with flag --exclude_head_nodes to explicitly
    # exclude head nodes from slurm reservation.
    echo "No free nodes available, restarting OPTIMA with --exclude_head_nodes"
    $OPTIMA_PATH --config {args.config} \\
                 --name {args.name} \\
                 --cluster {args.cluster} \\
                 --cpus {args.cpus} \\
                 --gpus {args.gpus} \
{_optional_argument_formatter("mem_per_cpu", args.mem_per_cpu)} \
{_optional_argument_formatter("cpus_per_worker", args.cpus_per_worker)} \
{_optional_argument_formatter("gpus_per_worker", args.gpus_per_worker)} \
{_optional_argument_formatter("workers", args.workers)} \
{_optional_argument_formatter("min_cpus_per_ray_node", args.min_cpus_per_ray_node)} \
{_optional_argument_formatter("fixed_ray_node_size", args.fixed_ray_node_size)} \\
                 --runtime {args.runtime} \\
                 --exclude_head_nodes \
{_optional_argument_formatter("exclude", ",".join(job.excludes_list))} \
{_optional_argument_formatter("apply_ulimit_fix", args.apply_ulimit_fix)} \\
                 --cpus_per_trial {args.cpus_per_trial} \\
                 --gpus_per_trial {args.gpus_per_trial} \
{_optional_argument_formatter("max_pending_trials", args.max_pending_trials)}
    exit 1
elif [ $EXIT_CODE -ne 0 ]; then
    echo "manage_ray_nodes exited with exit code $EXIT_CODE. Terminating..."
    exit $EXIT_CODE
fi

# read in the sorted list of nodes and cpus per node for this job
read nodes < temp_sorted_nodes_{cluster.get_job_id_bash()}.txt
read cpus_per_node < temp_sorted_cpus_per_node_{cluster.get_job_id_bash()}.txt
read instance_num < temp_instance_num_{cluster.get_job_id_bash()}.txt
nodes_array=($nodes)
cpus_per_node_array=($cpus_per_node)
echo "Nodes after sorting: $nodes"
echo "CPUs per node: $cpus_per_node"

# delete the temporary files that contained the sorted nodes list, the list of corresponding numbers of cpus and the instance_num
rm temp_sorted_nodes_{cluster.get_job_id_bash()}.txt
rm temp_sorted_cpus_per_node_{cluster.get_job_id_bash()}.txt
rm temp_instance_num_{cluster.get_job_id_bash()}.txt
"""

    ray_setup_str_2 = f"""head_node=${{nodes_array[0]}}
head_node_ip={cluster.get_node_ip_bash("$head_node")}

# if we detect a space character in the head node IP, we'll
# convert it to an ipv4 address. This step is optional.
if [[ "$head_node_ip" == *" "* ]]; then
IFS=' ' read -ra ADDR <<<"$head_node_ip"
if [[ ${{#ADDR[0]}} -gt 16 ]]; then
  head_node_ip=${{ADDR[1]}}
else
  head_node_ip=${{ADDR[0]}}
fi
echo "IPV6 address detected. We split the IPV4 address as $head_node_ip"
fi

port=$(({port_config["port"][0]}+{port_config["port"][1]}*$instance_num))
ip_head=$head_node_ip:$port
export ip_head
echo "IP Head: $ip_head"

echo "Starting HEAD at $head_node"
{cluster.start_ray_node(
        node="$head_node",
        head_ip="$head_node_ip",
        port=f"$(({port_config['port'][0]}+{port_config['port'][1]}*$instance_num))",
        node_manager_port=f"$(({port_config['node_manager_port'][0]}+{port_config['node_manager_port'][1]}*$instance_num))",
        object_manager_port=f"$(({port_config['object_manager_port'][0]}+{port_config['object_manager_port'][1]}*$instance_num))",
        ray_client_server_port=f"$(({port_config['ray_client_server_port'][0]}+{port_config['ray_client_server_port'][1]}*$instance_num))",
        redis_shard_ports=f"$(({port_config['redis_shard_ports'][0]}+{port_config['redis_shard_ports'][1]}*$instance_num))",
        min_worker_port=f"$(({port_config['min_worker_port'][0]}+{port_config['min_worker_port'][1]}*$instance_num))",
        max_worker_port=f"$(({port_config['max_worker_port'][0]}+{port_config['max_worker_port'][1]}*$instance_num))",
        num_cpus="${cpus_per_node_array[0]}" if not args.fixed_ray_node_size else args.cpus_per_worker,
        num_gpus=args.gpus_per_worker,
        head=True,
    )}

# optional, though may be useful in certain versions of Ray < 1.0.
sleep 30

# number of nodes other than the head node
worker_num=$((SLURM_JOB_NUM_NODES - 1))

for ((i = 1; i <= worker_num; i++)); do
    node_i=${{nodes_array[$i]}}
    echo "Starting WORKER $i at $node_i"
    this_node_ip={cluster.get_node_ip_bash("$node_i")}
    {cluster.start_ray_node(
        node="$node_i",
        head_ip="$ip_head",
        num_cpus="${cpus_per_node_array[$i]}" if not args.fixed_ray_node_size else args.cpus_per_worker,
        num_gpus=args.gpus_per_worker,
    )}
    sleep 5
done

sleep 30"""

    command_str = f"""# make sure stdout is directly written to log
export PYTHONUNBUFFERED=1

# do the optimization
$OPTIMA_PATH --config {args.config} \\
             --name {args.name} \\
             --cluster {args.cluster} \\
             --cpus {args.cpus} \\
             --gpus {args.gpus} \
{_optional_argument_formatter("mem_per_cpu", args.mem_per_cpu)} \
{_optional_argument_formatter("cpus_per_worker", args.cpus_per_worker)} \
{_optional_argument_formatter("gpus_per_worker", args.gpus_per_worker)} \
{_optional_argument_formatter("workers", args.workers)} \
{_optional_argument_formatter("min_cpus_per_ray_node", args.min_cpus_per_ray_node)} \
{_optional_argument_formatter("fixed_ray_node_size", args.fixed_ray_node_size)} \\
             --runtime {args.runtime} \
{_optional_argument_formatter("exclude_head_nodes", args.exclude_head_nodes)} \
{_optional_argument_formatter("exclude", ",".join(job.excludes_list))} \
{_optional_argument_formatter("apply_ulimit_fix", args.apply_ulimit_fix)} \\
             --cpus_per_trial {args.cpus_per_trial} \\
             --gpus_per_trial {args.gpus_per_trial} \
{_optional_argument_formatter("max_pending_trials", args.max_pending_trials)} \\
             --is_worker \\
             --address $ip_head"""

    # put all five parts together to build the job file
    job_str = """{environment}{ulimit}

{ray_setup_1}

{ray_setup_2}

{command}""".format(environment=environment_str, ulimit=ulimit_str, ray_setup_1=ray_setup_str_1, ray_setup_2=ray_setup_str_2,
               command=command_str)

    # create logs folder
    if not os.path.exists("logs"):
        os.makedirs("logs", exist_ok=True)

    # write copy of batch job file to output path for reproducibility
    job.payload = job_str
    output_dir = OPTIMA.core.tools.get_output_dir(run_config)
    cluster.submit_job(job, job_file_path=os.path.join(output_dir, "submit_DNNOptimization_ray.sh"), dry_run=True)

    # execute the job; do not overwrite existing batch scripts, instead append next free number
    i = 0
    while True:
        if not os.path.exists(f"submit_DNNOptimization_ray_{i}.sh"):
            cluster.submit_job(job, job_file_path=f"submit_DNNOptimization_ray_{i}.sh")
            break
        else:
            i += 1

    # once done, delete the batch script
    os.remove(f"submit_DNNOptimization_ray_{i}.sh")


def main():
    parser = argparse.ArgumentParser(description='Performs parallelized hyperparameter optimization of DNNs using Optuna and Population Based Training', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config", default='configs/config.py', help="Path to the run-config file to use.")
    parser.add_argument("--defaults", type=str, default=None, help="Path to a config file to be used as the defaults-config instead of the built-in defaults.")
    parser.add_argument("--name", default='DNN_optimization', help="Name for the job.")
    parser.add_argument('--cluster', default='local', help="Specify which cluster the job should be executed on. This must be one of the possible values given in get_cluster() in hardware_config.common, "
                                                                        "'local' to directly start a Ray head node and execute OPTIMA locally, or 'custom' when providing an own cluster via --cluster_config.")
    parser.add_argument('--cluster_config', type=str, default=None, help="Path to a file containing a Cluster subclass called 'CustomCluster' that defines a new cluster.")
    parser.add_argument('--cpus', type=int, default=1, help="Total number of CPUs in the cluster.")
    parser.add_argument('--gpus', type=int, default=0, help="Total number of gpus in the cluster. If >0, this implicitly sets --fixed_ray_node_size.")
    parser.add_argument('--mem_per_cpu', type=float, default=None, help="Amount of memory per CPU core (in MB). If not specified, will use the cluster limit when running on a cluster or 1000 MB when running locally.")
    parser.add_argument('--cpus_per_worker', type=int, default=None, help="Number of CPU cores per Ray node. Only used if --fixed_ray_node_size is given.")
    parser.add_argument('--gpus_per_worker', type=int, default=None, help="Number of gpus per Ray node. Only used if --fixed_ray_node_size is given.")
    parser.add_argument('--workers', type=int, default=None, help="Number of Ray nodes. Only used if --fixed_ray_node_size is given.")
    parser.add_argument("--min_cpus_per_ray_node", type=int, default=None, help="Minimum number of CPU cores that should be reserved per Ray node. This is not used if --fixed_ray_node_size is given.")
    parser.add_argument('--fixed_ray_node_size', default=False, action="store_true", help="If True, will enforce the same number of CPUs and gpus on each Ray node instead of letting the cluster management "
                                                                                          "software handle the allocation. This is implicitly set when gpus > 0.")
    parser.add_argument('--runtime', type=float, default=12., help="Runtime in hours for which the resources should be reserved.")

    parser.add_argument('--exclude_head_nodes', default=False, action="store_true", help="If True, will explicitly add machines that are already running head nodes to the --exclude parameter.")
    parser.add_argument('--exclude', default="", help="Comma seperated list of nodes that should be excluded from the job (e.g. nodes that are knows to cause problems)")
    parser.add_argument('--apply_ulimit_fix', default=False, action="store_true", help="Increase the user process limit, which can be necessary when running many trials on the same machine.")

    parser.add_argument('--cpus_per_trial', type=int, default=1, help="Number of CPUs that are used for each trial.")
    parser.add_argument('--gpus_per_trial', type=float, default=0.0, help="Number of GPUs that are used for each trial. This can be a fractional number to run multiple trials on each GPU.")
    parser.add_argument('--max_pending_trials', type=int, default=None, help="Set how many trials are allowed to be 'pending'. If not set, will set to cpus / cpus_per_trail.")

    parser.add_argument('--is_worker', default=False, action="store_true", help="Is used to differentiate between the initialization step (create and execute batch script) and the working step (where the optimization is done).")
    parser.add_argument('--address', default=None, help="IP-address and port of the head node. This is set automatically for the working step.")
    parser.add_argument('--local_source', default=False, action="store_true", help="If set, will use the local source code even if OPTIMA is installed in the python environment.")
    parser.add_argument('--temp_dir', type=str, default=None, help="Overwrite Ray's default root temporary directory when running locally (i.e. --cluster 'local'). This must be an absolute path.")

    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args(sys.argv[1:])

    # logging config
    DFormat = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=DFormat, level=logging.INFO)

    # load and check the config
    # import the config file
    import importlib.util
    run_config_spec = importlib.util.spec_from_file_location("config", args.config)
    run_config = importlib.util.module_from_spec(run_config_spec)
    # sys.modules["config"] = run_config  # not needed because config is a single file, not a package + caused problems when reloading scaler!
    run_config_spec.loader.exec_module(run_config)

    # import the defaults
    import inspect
    if args.defaults is not None:
        defaults_spec = importlib.util.spec_from_file_location("defaults", args.defaults)
        defaults = importlib.util.module_from_spec(defaults_spec)
        defaults_spec.loader.exec_module(defaults)
        with open(args.defaults, "r") as f:
            defaults_config_str = f.read()
    else:
        import OPTIMA.defaults as defaults
        defaults_config_str = inspect.getsource(defaults)

    # add missing config entries from defaults by going through the attributes of the default config and checking if it is
    # also present in the run-config.
    for param, value in defaults.__dict__.items():
        if not (inspect.ismodule(value) or inspect.isbuiltin(value) or param[:2] == "__"):
            if param not in run_config.__dict__.keys():
                setattr(run_config, param, value)

    # check that all required parameters are provided
    param_missing = False
    for param in defaults.__requires__:
        if param not in run_config.__dict__.keys():
            logging.critical(f"Required parameter '{param}' was not provided in the run-config.")
            param_missing = True

    # check that all parameters required by used built-in functionality are provided
    for builtin_func_tuple, param in defaults.__requires_builtin__:
        if param not in run_config.__dict__.keys():
            # iterate over all builtin functions that require this parameter and check if all of them are overwritten
            unsatisfied_builtin_funcs = []
            for builtin_func in builtin_func_tuple:
                if not hasattr(run_config, builtin_func):
                    unsatisfied_builtin_funcs.append(builtin_func)
            if len(unsatisfied_builtin_funcs) > 0:
                logging.critical(f"Parameter '{param}', which is required by built-in functionality "
                                 f"({' & '.join(unsatisfied_builtin_funcs)}), was not provided in the run-config.")
                param_missing = True

    # check that all parameters required when running on a cluster are provided
    if args.cluster != "local":
        for param in defaults.__requires_cluster__:
            if param not in run_config.__dict__.keys():
                logging.critical(f"Parameter '{param}' is required when running on a cluster but was not provided in the run-config.")
                param_missing = True

    if param_missing:
        sys.exit(1)

    # get the cluster and perform sanity checks in the requested cluster parameters
    if args.cluster != "local":
        if args.cluster == "custom":
            if args.cluster_config is None:
                logging.critical("Parameter --cluster is set to 'custom' but no cluster config file is provided.")
                sys.exit(1)

            # load the custom cluster class
            custom_cluster_config_spec = importlib.util.spec_from_file_location("custom_cluster_config", args.cluster_config)
            custom_cluster_config = importlib.util.module_from_spec(custom_cluster_config_spec)
            custom_cluster_config_spec.loader.exec_module(custom_cluster_config)
            cluster = custom_cluster_config.CustomCluster()
        else:
            # load the built-in cluster class
            cluster = get_cluster(args.cluster)

        # start with same-sized fixed Ray nodes
        if args.fixed_ray_node_size or args.gpus > 0 or (args.gpus_per_worker > 0 if args.gpus_per_worker is not None else False):
            if not args.fixed_ray_node_size:
                logging.warning("Variable CPUs per Ray node are only supported when not using GPUs. Implicitly settings the --fixed_ray_node_size flag.")

            # first check if cluster limits are fulfilled
            if args.cpus_per_worker is not None:
                if args.cpus_per_worker > cluster.cpus_per_node:
                    logging.warning(f"Requested CPUs per Ray node of {args.cpus_per_worker} exceeds the cluster limit of {cluster.cpus_per_node}. Limiting to the cluster limit...")
                    args.cpus_per_worker = cluster.cpus_per_node
            if args.gpus_per_worker is not None:
                if args.gpus_per_worker > cluster.gpus_per_node:
                    logging.warning(f"Requested GPUs per Ray node of {args.gpus_per_worker} exceeds the cluster limit of {cluster.gpus_per_node}. Limiting to the cluster limit...")
                    args.gpus_per_worker = cluster.gpus_per_node
            if args.mem_per_cpu is not None:
                if args.mem_per_cpu > cluster.mem_per_cpu:
                    logging.warning(f"Requested memory per CPU core of {args.mem_per_cpu} exceeds the cluster limit of {cluster.mem_per_cpu}. Limiting to the cluster limit...")
                    args.mem_per_cpu = cluster.mem_per_cpu

            # next calculate possible missing parameters
            # start with only number of cpus
            if args.cpus is not None and args.cpus_per_worker is None and args.workers is None:
                if args.cpus < cluster.cpus_per_node:
                    args.cpus_per_worker = args.cpus
                    args.workers = 1
                else:
                    args.workers = int(np.ceil(args.cpus / cluster.cpus_per_node))
                    args.cpus_per_worker = int(np.ceil(args.cpus / args.workers))
                    cpus = int(args.workers * args.cpus_per_worker)
                    if cpus != args.cpus:
                        print(f"Cannot fulfill CPU request of {args.cpus} CPU cores while respecting the cluster limit of "
                              f"{cluster.cpus_per_node} cores per node and ensuring the same number of cores for each "
                              f"worker. Will instead use {cpus} CPU cores, distributed evenly across {args.workers} workers.")
                        args.cpus = cpus

            # only number of gpus
            if args.gpus is not None and args.gpus_per_worker is None and args.workers is None:
                if args.gpus < cluster.gpus_per_node:
                    args.gpus_per_worker = args.gpus
                    args.workers = 1
                else:
                    args.workers = int(np.ceil(args.gpus / cluster.gpus_per_node))
                    args.gpus_per_worker = int(np.ceil(args.gpus / args.workers))
                    gpus = int(args.workers * args.gpus_per_worker)
                    if gpus != args.gpus:
                        print(f"Cannot fulfill GPU request of {args.gpus} GPUs while respecting the cluster limit of "
                              f"{cluster.gpus_per_node} GPUs per node and ensuring the same number of cores for each "
                              f"worker. Will instead use {gpus} GPUs, distributed evenly across {args.workers} workers.")
                        args.gpus = gpus

            # CPUs and CPUs / node given
            if args.cpus is not None and args.cpus_per_worker is not None and args.workers is None:
                if args.cpus % args.cpus_per_worker == 0:
                    args.workers = int(args.cpus / args.cpus_per_worker)
                else:
                    args.workers = int(args.cpus / args.cpus_per_worker) + 1
                    logging.warning(f"Number of CPUs of {args.cpus} and number of CPUs per node of {args.cpus_per_worker} "
                                    f"do not result in a whole number of nodes, rounding up to {args.workers} nodes.")

            # GPUs and GPUs / node
            if args.gpus is not None and args.gpus_per_worker is not None and args.workers is None:
                    if args.gpus % args.gpus_per_worker == 0:
                        args.workers = int(args.gpus / args.gpus_per_worker)
                    else:
                        args.workers = int(args.gpus / args.gpus_per_worker) + 1
                        logging.warning(f"Number of GPUs of {args.gpus} and number of GPUs per node of {args.gpus_per_worker} "
                                        f"do not result in a whole number of nodes, rounding up to {args.workers} nodes.")

            # number of nodes and CPUs / node
            if args.workers is not None and args.cpus_per_worker is not None and args.cpus is None:
                args.cpus = int(args.workers * args.cpus_per_worker)

            # number of nodes and GPUs / node
            if args.workers is not None and args.gpus_per_worker is not None and args.gpus is None:
                args.gpus = int(args.workers * args.gpus_per_worker)

            # number of nodes and number of CPUs
            if args.workers is not None and args.cpus is not None and args.cpus_per_worker is None:
                if args.cpus % args.workers == 0:
                    args.cpus_per_worker = int(args.cpus / args.workers)
                else:
                    args.cpus_per_worker = int(args.cpus / args.workers) + 1
                    logging.warning(f"Provided number of CPUs of {args.cpus} and number of nodes of {args.workers} result "
                                    f"in a non-integer number of CPUs per node. Rounding up to {args.cpus_per_worker} CPUs "
                                    f"per node, giving {int(args.workers * args.cpus_per_worker)} CPUs in total.")
                    args.cpus = int(args.workers * args.cpus_per_worker)

                if args.cpus_per_worker > cluster.cpus_per_node:
                    logging.critical(f"The provided number of CPUs of {args.cpus} and number of nodes of {args.workers} "
                                     f"results in a number of CPUs per node of {args.cpus_per_worker}, which exceeds the "
                                     f"cluster limit of {cluster.cpus_per_node}.")
                    sys.exit(1)

            # number of nodes and number of GPUs
            if args.workers is not None and args.gpus is not None and args.gpus_per_worker is None:
                if args.gpus % args.workers == 0:
                    args.gpus_per_worker = int(args.gpus / args.workers)
                else:
                    args.gpus_per_worker = int(args.gpus / args.workers) + 1
                    logging.warning(f"Provided number of GPUs of {args.gpus} and number of nodes of {args.workers} result "
                                    f"in a non-integer number of GPUs per node. Rounding up to {args.gpus_per_worker} GPUs "
                                    f"per node, giving {int(args.workers * args.gpus_per_worker)} CPUs in total.")
                    args.gpus = int(args.workers * args.gpus_per_worker)

                if args.gpus_per_worker > cluster.gpus_per_node:
                    logging.critical(f"The provided number of GPUs of {args.gpus} and number of nodes of {args.workers} "
                                     f"results in a number of GPUs per node of {args.gpus_per_worker}, which exceeds the "
                                     f"cluster limit of {cluster.gpus_per_node}.")
                    sys.exit(1)

            # consistency: CPU
            if args.cpus // args.cpus_per_worker != args.workers:
                logging.critical(f"Number of CPUs of {args.cpus}, number of CPUs per node of {args.cpus_per_worker} "
                                 f"and number of nodes of {args.workers} are not consistent, i.e. num_nodes * num_cpus_per_node != num_cpus!")
                sys.exit(1)

            # consistency: GPU
            if args.gpus > 0 and args.gpus // args.gpus_per_worker != args.workers:
                logging.critical(f"Number of GPUs of {args.gpus}, number of GPUs per node of {args.gpus_per_worker} "
                                 f"and number of nodes of {args.workers} are not consistent, i.e. num_nodes * num_gpus_per_node != num_gpus!")
                sys.exit(1)
        else:
            # number of cpus needs to be specified for variable node size to work!
            if args.cpus is None:
                logging.critical(f"The number of CPU cores need to be specified for the variable Ray node size to work!")
                sys.exit(1)

            # minimum node size needs to be specified as well
            if args.min_cpus_per_ray_node is None:
                logging.critical(f"The minimum Ray node size must be given by specifying --min_cpus_per_ray_node!")
                sys.exit(1)

            # ensure the minimum node sizes are compatible with cluster limits
            if args.min_cpus_per_ray_node > cluster.cpus_per_node:
                logging.warning(f"min_cpus_per_ray_node is set to a value of {args.min_cpus_per_ray_node} which exceeds "
                                f"the cluster limit of {cluster.cpus_per_node} CPUs per node. Limiting min_cpus_per_ray_node "
                                f"to {cluster.cpus_per_node}.")
                args.min_cpus_per_ray_node = cluster.cpus_per_node

            # make sure the minimum node sizes allows dividing the total resource request into smaller tasks, for which
            # multiple can be scheduled on the same node
            if args.cpus % args.min_cpus_per_ray_node != 0:
                args.cpus = int(np.ceil(args.cpus / args.min_cpus_per_ray_node) * args.min_cpus_per_ray_node)
                logging.warning(f"To allow variable node sizes, the total number of CPU cores needs to be divisible "
                                f"by the minimum number of CPUs per Ray node. Rounding to the nearest higher value of "
                                f"{args.cpus} CPU cores.")

            # explicitly setting cpus per worker and number of workers to impossible values and set gpus_per_worker to 0.
            args.cpus_per_worker = -1
            args.gpus_per_worker = 0
            args.workers = -1

    # check if mem_per_cpus set and within cluster limits
    if args.mem_per_cpu is not None and args.cluster != "local":
        if args.mem_per_cpu > cluster.mem_per_cpu:
            logging.warning(f"Provided --mem_per_cpu of {args.mem_per_cpu} exceeds the cluster limit of {cluster.mem_per_cpu}. "
                            f"Limiting to {cluster.mem_per_cpu}")
            args.mem_per_cpu = cluster.mem_per_cpu
    elif args.cluster != "local":
        args.mem_per_cpu = cluster.mem_per_cpu
    elif args.mem_per_cpu is None:
        logging.info("Setting mem_per_cpu to 1000 MB.")
        args.mem_per_cpu = 1000

    # set the maximum number of pending trials
    if args.max_pending_trials is not None:
        os.environ['TUNE_MAX_PENDING_TRIALS_PG'] = f'{args.max_pending_trials}'
    else:
        args.max_pending_trials = int(args.cpus / args.cpus_per_trial)
        print(f"Setting the maximum number of pending trials to CPUs / cpus_per_trial = {args.max_pending_trials}.")
        os.environ['TUNE_MAX_PENDING_TRIALS_PG'] = f'{args.max_pending_trials}'

    if not args.is_worker and not args.cluster == "local":
        initialize(args, run_config, cluster, custom_cluster_config=custom_cluster_config if args.cluster_config is not None else None)
    else:
        do_optimization(args, run_config, defaults_config_str, cluster if args.cluster != "local" else None)
