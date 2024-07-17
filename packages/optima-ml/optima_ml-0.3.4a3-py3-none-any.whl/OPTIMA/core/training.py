# -*- coding: utf-8 -*-
"""A module that provides general functionality for the training and crossvalidation."""
import logging
import os
import json
import pickle
import shutil
import sys
import time
from functools import partial

if sys.platform == "darwin":
    from multiprocess import parent_process
    from multiprocess.synchronize import Event
    from multiprocess.queues import Queue
else:
    from multiprocessing import parent_process
    from multiprocessing.synchronize import Event
    from multiprocessing.queues import Queue

from types import ModuleType
from typing import Union, Optional, Callable, Any, Literal

from abc import ABC, abstractmethod
import numpy as np

import ray
from ray import train, tune

import OPTIMA.core.inputs
import OPTIMA.core.tools
import OPTIMA.builtin.inputs
from OPTIMA.core.model import model_config_type

import importlib.util

if importlib.util.find_spec("tensorflow") is not None:
    import OPTIMA.keras.tools


class EarlyStopperForTuning(ABC):
    """Abstract base class to do early stopping based on custom/composite metrics and overfitting conditions for Tune experiments.

    This, amongst others, includes the reporting to `Tune`, saving of checkpoints and the ability to load and save the
    state of the early stopper. Additionally, it allows to calculate the values of two additional types of metrics.
    Firstly, `custom metrics` are metrics whose value can be determined from the predictions of the model, the corresponding
    target labels and sample weights. Their values are calculated at the end of each epoch for both the training and the
    validation dataset. Secondly, `composite metrics` are metrics whose values can be calculated from already existing
    metrics. This includes e.g. also metrics whose values are determined by the value of a `custom metric` on both the
    training and validation datasets. Both types of metrics can be used as target metrics and / or to define `overfitting
    conditions`.

    Since this class is independent of the machine learning library used, metrics that are directly reported during the
    training or validation are referred to as `native metrics`.
    """

    def __init__(
        self,
        monitor: tuple[str, str] = ("val_loss", "min"),
        min_delta: Union[int, float] = 0,
        metrics: Optional[list[str]] = None,
        weighted_metrics: Optional[list[str]] = None,
        custom_metrics: Optional[list[tuple[str, Callable]]] = None,
        composite_metrics: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
        overfitting_conditions: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
        patience_improvement: int = 0,
        patience_overfitting: int = 0,
        inputs_train: Optional[Any] = None,
        targets_train: Optional[Any] = None,
        weights_train: Optional[Any] = None,
        inputs_val: Optional[Any] = None,
        targets_val: Optional[Any] = None,
        weights_val: Optional[Any] = None,
        restore_best_weights: bool = False,
        create_checkpoints: bool = True,
        checkpoint_dir: Optional[str] = None,
        first_checkpoint_epoch: int = 1,
        checkpoint_frequency: int = 1,
        report_event: Optional[Event] = None,
        report_queue: Optional[Queue] = None,
        report_queue_read_event: Optional[Event] = None,
        termination_event: Optional[Event] = None,
        in_tune_session: bool = True,
        verbose: int = 0,
    ) -> None:
        """Constructor of ``EarlyStopperForTuning``.

        Parameters
        ----------
        monitor : tuple[str, str]
            Tuple containing the name of the target metric and either ``'min'`` or ``'max'`` to signify if this metric
            is to be minimized or maximized. (Default value = ("val_loss", "min"))
        min_delta : Union[int, float]
            Minimum change in the target metric to qualify as an improvement, i.e. an absolute change of less than
            ``min_delta``, will count as no improvement. (Default value = 0)
        metrics : Optional[list[str]]
            A list of metric names. For each, two entries are expected in the ``logs``, one for the training metric value
            (with the same key as the metric name), and one for the validation metric value (key with ``'val_'``-prefix).
            When added to the results, a ``'train_``-prefix is added to the training metric value. (Default value = None)
        weighted_metrics : Optional[list[str]]
            A list of metric names. For each, two entries are expected in the ``logs``, one for the training metric value
            (with the same key as the metric name), and one for the validation metric value (key with ``'val_'``-prefix).
            When added to the results, a ``'train_``-prefix is added to the training metric value. (Default value = None)
        custom_metrics : Optional[list[tuple[str, Callable]]]
            A list of tuples. Each tuple has to contain a name for this metric that will be used to add its value to the
            ``logs`` (with ``'train_'`` and ``'val_'`` prefixes), and a callable with the signature
            ``(y_true, y_pred, sample_weight)``, i.e. it has to accept the array of target labels, the array of
            corresponding predictions and the array of sample weights. The callable has to return either a number or a
            bool. The value of this metric is calculated at the end of each epoch separately on the training and
            validation datasets. (Default value = None)
        composite_metrics : Optional[list[tuple[str, tuple[str, str], Callable]]]
            A list of tuples. Each tuple has to contain a name for this metric that will be used to add its value to the
            ``logs`` (with ``'train_'`` and ``'val_'`` prefixes), a tuple containing the names of already existing
            metrics (i.e. need to be available in the ``logs`` or be in ``custom_metrics``), and a callable that has to
            accept the values of the metrics whose names are provided as positional arguments. The callable has to return
            either a number or a bool. (Default value = None)
        overfitting_conditions : Optional[list[tuple[str, tuple[str, str], Callable]]]
            A list of tuples. Each tuple has to contain the names of two already existing metrics (i.e. need to be
            available in the ``logs`` or be in ``custom_metrics``) and a callable that has to accept the values of these
            metrics. The callable has to return a bool which should be ``True`` if the generalization gap is too large.
            (Default value = None)
        patience_improvement : int
            Number of epochs to wait for improvement of the target metric before terminating the training. (Default value = 0)
        patience_overfitting : int
            Number of epochs to continue training when at least one of the overfitting conditions returned ``True``. (Default value = 0)
        inputs_train : Optional[Any]
            Data structure containing the input features of the training dataset. (Default value = None)
        targets_train : Optional[Any]
            Data structure containing the target labels of the training dataset. (Default value = None)
        weights_train : Optional[Any]
            Data structure containing the event weights of the training dataset. (Default value = None)
        inputs_val : Optional[Any]
            Data structure containing the input features of the validation dataset. (Default value = None)
        targets_val : Optional[Any]
            Data structure containing the target labels of the validation dataset. (Default value = None)
        weights_val : Optional[Any]
            Data structure containing the event weights of the validation dataset. (Default value = None)
        restore_best_weights : bool
            Whether to restore model weights from the epoch with the best value of the target metric. If ``False``, the
            model weights obtained at the last step of training are used. (Default value = False)
        create_checkpoints : bool
            Whether to save a checkpoint of the current and best model and the state of the early stopper at the end of
            each epoch. (Default value = True)
        checkpoint_dir : Optional[str]
            An optional path to the directory the model checkpoints should be saved to. If ``None``, a new directory
            ``'checkpoint_dir'`` is created in the current working directory. (Default value = None)
        first_checkpoint_epoch : int
            The first epoch after which a checkpoint should be saved. (Default value = 1)
        checkpoint_frequency : int
            Controls how often a checkpoint of the model weights and the early stopper state are saved. If the current
            epoch number (when starting to count from 1) minus the ``first_checkpoint_epoch`` is divisible by
            ``checkpoint_frequency``, a checkpoint is created. (Default value = 1)
        report_event : Optional[Event]
            `Multiprocessing` ``event`` triggered to tell the parent process the results dictionary has been added to the
            ``report_queue``. If not provided, report results directly to Tune. (Default value = None)
        report_queue : Optional[Queue]
            `Multiprocessing` ``queue`` to send the current epoch number and the results dictionary to the parent
            process. If not provided, report results directly to Tune. (Default value = None)
        report_queue_read_event : Optional[Event]
            `Multiprocessing` ``event`` triggered by the parent process when the results dictionary has been read from the
            ``report_queue`` and reported to `Tune`. If not provided, report results directly to Tune. (Default value = None)
        termination_event : Optional[Event]
            `Multiprocessing` ``event`` triggered by the parent process to signify that the training should be terminated. (Default value = None)
        in_tune_session : bool
            If not in a `Tune` session, no results need to be reported. (Default value = True)
        verbose : int
            Verbosity mode, 0 or 1. Mode 0 is silent, and mode 1 displays messages when the callback takes an action. (Default value = 0)
        """
        if overfitting_conditions is None:
            overfitting_conditions = []
        if metrics is None:
            metrics = []
        if weighted_metrics is None:
            weighted_metrics = []
        if composite_metrics is None:
            composite_metrics = []
        if custom_metrics is None:
            custom_metrics = []

        # list of metrics that will be reported to Tune
        self.metrics = metrics
        self.weighted_metrics = weighted_metrics
        self.custom_metrics = custom_metrics
        self.composite_metrics = composite_metrics

        # core settings for the early stopping
        self.monitor = monitor[0]
        if monitor[1] == "min":
            self.monitor_op = np.less
        elif monitor[1] == "max":
            self.monitor_op = np.greater
        else:
            logging.warning(f"Mode {monitor[1]} is not known, falling back to 'min'.")
            self.monitor_op = np.less
        self.min_delta = min_delta
        self.patience_improvement = patience_improvement
        self.patience_overfitting = patience_overfitting
        self.overfitting_conditions = overfitting_conditions

        # various other settings
        self.create_checkpoints = create_checkpoints
        self.checkpoint_dir = checkpoint_dir if checkpoint_dir is not None else "checkpoint_dir"
        self.first_checkpoint_epoch = first_checkpoint_epoch
        self.checkpoint_frequency = checkpoint_frequency
        self.restore_best_weights = restore_best_weights
        self.verbose = verbose

        # status variables to keep track of the current status of the optimization
        self.current_epoch = 0
        self.wait = 0
        self.wait_overfitting = 0
        self.best = np.Inf if self.monitor_op == np.less else -np.Inf
        self.best_metrics = (
            {}
        )  # will contain the values of the metrics for the best epoch (epoch with best monitor value)
        self.best_weighted_metrics = (
            {}
        )  # will contain the values of the weighted metrics for the best epoch (epoch with best monitor value)
        self.best_custom_metrics = (
            {}
        )  # will contain the values of the custom metrics for the best epoch (epoch with best monitor value)
        self.best_composite_metrics = (
            {}
        )  # will contain the values of the composite metrics for the best epoch (epoch with best monitor value)
        self.best_epoch = 0
        self.stopped_epoch = 0
        self.early_stopped = False
        self.best_weights = None

        # even when reporting the current values instead of the best, we cannot carelessly report the actual current value
        # because that would make checking the overtraining conditions mostly useless. we therefore store "valid" values
        # that are the current values if no overtraining is present, and the last valid value when overtraining is present
        # --> prevents overtrained epochs from having better metric than previous non-overtrained epoch
        self.last_valid = np.Inf if self.monitor_op == np.less else -np.Inf

        # training and validation datasets for calculating custom metrics
        self.inputs_train = inputs_train
        self.targets_train = targets_train
        self.weights_train = weights_train
        self.inputs_val = inputs_val
        self.targets_val = targets_val
        self.weights_val = weights_val

        # events and queue for inter-process reporting
        if (
            report_event is not None
            and report_queue is not None
            and report_queue_read_event is not None
            and termination_event is not None
        ):
            self.report_directly = False  # assume we are running in a subprocess and cannot report directly to Tune
            self.report_event = report_event
            self.report_queue = report_queue
            self.report_queue_read_event = report_queue_read_event
            self.termination_event = termination_event
        else:
            self.report_directly = True  # report directly to Tune

        # If False, do not report to Tune at all
        self.in_tune_session = in_tune_session

        # get the id of the main process to check if it is terminated (in case the subprocess termination fails and this
        # process keeps hanging)
        self.parent_process = parent_process()

    def at_epoch_end(self, epoch: int, logs: Optional[dict] = None, **kwargs: dict) -> None:
        """Calculates `custom` and `composite metrics`, performs the early stopping, saves checkpoints and reports to `Tune`.

        The values of the `custom` and `composite metrics` (if provided) are calculated and added to the ``logs`` dictionary
        before calling ``on_epoch_end of`` the `super`-class which performs the early stopping based on the provided metrics,
        and the `overfitting conditions`.

        If ``self.create_checkpoints`` is ``True``, the current model, the best model and the state of the
        ``EarlyStopperForTuning``-instance (i.e. the objects returned by ``self.get_state``) are saved to disk. If an
        improvement of the target metric was observed, the best model is updated to the current model before saving.

        If ``self.in_tune_session`` is ``True``, the metric values need to be reported to Tune. After building a dictionary
        containing the results (i.e. calling ``self.build_results_dict``), two cases are distinguished:

        - ``self.report_directly`` is ``False``: Multiprocessing events and queues were provided for the communication,
          implying that we are running in a subprocess. The dictionary containing the current results is added to the
          ``self.report_queue`` and the ``self.report_event`` is triggered. The parent process is expected to take the
          results from the queue and report them to `Tune`. This cannot be done directly as `Tune` seems to associate
          each trial with the corresponding process-id and thus would not recognize the report. After triggering the
          ``self.report_event``, this function waits for up to 600 seconds for the ``self.report_queue_read_event`` to
          be triggered, which is used to signify that the results have been successfully reported to `Tune`. After 120
          seconds of waiting, the status of the parent process is checked in a one-second interval. If the parent process
          is not alive anymore, this process self-terminates. After 600 seconds of waiting, the self-termination is also
          triggered even if the parent process is still alive. Once the ``self.report_queue_read_event`` is triggered,
          it is cleared and the function returns.
        - ``self.report_directly`` is ``True``: Multiprocessing events and queues were not provided, thus a checkpoint is
          built from the ``self.checkpoint_dir`` directory and the results dictionary and the checkpoint are reported
          directly to `Tune`.

        Parameters
        ----------
        epoch : int
            The number of epochs since the start of the training.
        logs : Optional[dict]
            Dictionary containing the metrics reported during training and validation. (Default value = None)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        # update the current epoch. The value given here as epoch is the epoch number of the just finished epoch. Since
        # the "current" epoch is the next one, we need to add one.
        self.current_epoch = epoch + 1

        # calculate all custom metrics on both training and validation data and add them to this epoch's logs
        if len(self.custom_metrics) > 0:
            logs = self.calc_custom_metrics(logs, **kwargs)

        # calculate the composite metrics
        if len(self.composite_metrics) > 0:
            logs = self.calc_composite_metrics(logs, **kwargs)

        # do the early stopping including updating the status variables. If the training should be terminated due to
        # early stopping, this internally calls self.stop_training()
        is_improvement = self._do_early_stopping(epoch, logs, **kwargs)

        # checkpoint the model and the early stopper status if checkpoints are requested. For this, a directory in the
        # current working dir (which is specific for this trial) is created and the current model, the best model and
        # the early stopper state is dumped there
        if (
            self.create_checkpoints
            and epoch + 1 >= self.first_checkpoint_epoch
            and (epoch + 1 - self.first_checkpoint_epoch) % self.checkpoint_frequency == 0
        ):
            # save current model
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            self.save_model(output_dir=self.checkpoint_dir, model_name="model", **kwargs)

            # save model again as best model if there was an improvement; TODO: replace this with a copy?
            if is_improvement or epoch + 1 == self.first_checkpoint_epoch:
                self.save_model(output_dir=self.checkpoint_dir, model_name="best_model", **kwargs)

            # save early stopper state
            self.save_state(path=os.path.join(self.checkpoint_dir, "early_stopper"), **kwargs)

        # report to Tune if we are in a Tune session
        if self.in_tune_session:
            (
                current_metrics,
                current_weighted_metrics,
                current_custom,
                current_composite,
            ) = self._fetch_current_metric_values(logs, **kwargs)
            results = self.build_results_dict(
                logs,
                current_metrics,
                current_weighted_metrics,
                current_custom,
                current_composite,
                **kwargs,
            )

            # report the results back to tune by activating the report event and putting the results into the queue
            if self.report_directly:
                time_before_report = time.time()
                if (
                    self.create_checkpoints
                    and epoch + 1 >= self.first_checkpoint_epoch
                    and (epoch + 1 - self.first_checkpoint_epoch) % self.checkpoint_frequency == 0
                ):
                    checkpoint = train.Checkpoint.from_directory(self.checkpoint_dir)
                    train.report(results, checkpoint=checkpoint)
                else:
                    train.report(results)
                if time.time() - time_before_report > 2:
                    logging.warning(
                        "Reporting results took {} seconds, which may be a performance bottleneck.".format(
                            time.time() - time_before_report
                        )
                    )
            else:
                self.report_queue.put((epoch, results))
                self.report_event.set()

                # wait until the report_queue_read_event is set. When tune terminates the trial, this process should also
                # be terminated externally, so we usually don't have to take care of that here. However sometimes this
                # termination fails, which we unfortunately can only detect once the parent process is terminated, which
                # would be too late. We still check, if the main process is still alive (in case it is killed or an error
                # occurs), but limit the time or waiting to a total 600 seconds before this subprocess self-terminates
                self.report_queue_read_event.wait(timeout=120)
                wait_start_time = time.time() - 120
                while not self.report_queue_read_event.is_set():
                    if self.parent_process is not None:
                        if not self.parent_process.is_alive():
                            sys.exit(0)
                    if time.time() - wait_start_time > 600:
                        self.termination_event.set()
                        sys.exit(0)
                    time.sleep(1)
                self.report_queue_read_event.clear()

    def _do_early_stopping(self, epoch, logs=None, **kwargs: dict) -> bool:
        """Internal method that actually does the early stopping and updating of the state variables.

        Parameters
        ----------
        epoch : int
            The number of epochs since the start of the training.
        logs : Optional[dict]
            Dictionary containing the metrics reported during training and validation. (Default value = None)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        bool
            ``True`` if an improvement of the target metric was seen without violating any overfitting conditions,
            ``False`` otherwise.
        """
        # get the current value of the metric to monitor
        current = self.get_monitor_value(logs, **kwargs)
        if current is None:
            # If no monitor value exists or still in initial warm-up stage.
            return False

        # get the best weights after the first epoch in case no progress is ever made
        if self.restore_best_weights and self.best_weights is None:
            self.best_weights = self.get_weights(**kwargs)

        # update waits and check improvement and overfitting conditions
        self.wait += 1
        self.wait_overfitting += 1
        is_improvement = self._is_improvement(current, self.best, **kwargs)
        is_overfit, overfitting_reasons = self._is_overfit(logs, **kwargs)

        # if both improvement and not overfit, update the early stopper state. This also fetches the current model weights
        # and saves them as self.best_weights.
        if is_improvement and not is_overfit:
            if self.verbose > 0:
                print("Epoch {}: Model improved from {:.5f} to {:.5f}".format(epoch + 1, self.best, current))
            self.best = current
            self.last_valid = current
            self.best_epoch = epoch
            if self.restore_best_weights:
                self.best_weights = self.get_weights(**kwargs)

            # update the best metric values
            (
                current_metrics,
                current_weighted_metrics,
                current_custom,
                current_composite,
            ) = self._fetch_current_metric_values(logs, **kwargs)
            self.best_metrics = current_metrics
            self.best_weighted_metrics = current_weighted_metrics
            self.best_custom_metrics = current_custom
            self.best_composite_metrics = current_composite
        if not is_improvement and not is_overfit:
            self.last_valid = current  # still update the last valid metric value as we do not have overfitting
            if self.verbose > 0:
                print("Epoch {}: Model did not improve from {:.5f}".format(epoch + 1, self.best))
        if is_overfit and self.verbose > 0:
            print("Epoch {}: Model is overfitted, reason: {}".format(epoch + 1, " & ".join(overfitting_reasons)))

        # independently reset the waits for improvement and overfitting
        if is_improvement:
            self.wait = 0
        if not is_overfit:
            self.wait_overfitting = 0

        # if either of the waits is larger than the patience, and it's not the first epoch, terminate. If requested,
        # overwrite the model weights with the weights saved at self.best_weights.
        if self.wait >= self.patience_improvement or self.wait_overfitting >= self.patience_overfitting and epoch > 0:
            self.stopped_epoch = epoch
            self.early_stopped = True
            self.stop_training(**kwargs)
            if self.restore_best_weights and self.best_weights is not None:
                if self.verbose > 0:
                    print("Restoring model weights from the end of the best epoch: " f"{self.best_epoch + 1}")
                self.set_weights(self.best_weights, **kwargs)

        # return if we have a true improvement
        return is_improvement and not is_overfit

    def _fetch_current_metric_values(
        self, logs: Optional[dict] = None, **kwargs: dict
    ) -> tuple[dict, dict, dict, dict]:
        """Fetches the `native`, `weighted native`, `custom` and `composite` metrics from the ``logs``.

        Parameters
        ----------
        logs : Optional[dict]
            Dictionary containing the metrics reported during training and validation. (Default value = None)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        tuple[dict, dict, dict, dict]
            The dictionary of `native`, `weighted native`, `custom` and `composite` metrics.
        """
        # start with the current native and weighted native metrics
        current_metrics = {}
        for metric in self.metrics:
            # get the metric names
            train_metric_name, val_metric_name = self.get_train_val_metric_names(metric, **kwargs)

            # metric to monitor could be a native metric --> we don't need that twice
            if not self.monitor == "train_" + metric:
                current_metrics["train_" + metric] = logs.get(train_metric_name)
            if not self.monitor == "val_" + metric:
                current_metrics["val_" + metric] = logs.get(val_metric_name)

        current_weighted_metrics = {}
        for metric in self.weighted_metrics:
            # get the metric names
            train_metric_name, val_metric_name = self.get_train_val_metric_names(metric, **kwargs)

            # metric to monitor could be a weighted native metric --> we don't need that twice
            if not self.monitor == "train_" + metric:
                current_weighted_metrics["train_" + metric] = logs.get(train_metric_name)
            if not self.monitor == "val_" + metric:
                current_weighted_metrics["val_" + metric] = logs.get(val_metric_name)

        # create a dict containing the current values of all custom metrics; will be used to overwrite self.custom_best
        # (if monitor value improved) and to report back to tune
        current_custom = {}
        for metric_name, _ in self.custom_metrics:
            # metric to monitor could be a custom metric --> we don't need that twice
            if not self.monitor == "train_" + metric_name:
                current_custom["train_" + metric_name] = logs.get("train_" + metric_name)
            if not self.monitor == "val_" + metric_name:
                current_custom["val_" + metric_name] = logs.get("val_" + metric_name)

        # now do the same for the composite metrics
        current_composite = {}
        for metric_name, _, _ in self.composite_metrics:
            # metric to monitor could be a composite metric --> we don't need that twice
            if not self.monitor == metric_name:
                current_composite[metric_name] = logs.get(metric_name)

        return current_metrics, current_weighted_metrics, current_custom, current_composite

    def get_monitor_value(self, logs: Optional[dict] = None, **kwargs: dict) -> Union[int, float]:
        """Helper function to fetch the current value of the metric to monitor.

        Parameters
        ----------
        logs : Optional[dict]
            Dictionary containing the metrics reported during training and validation. (Default value = None)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        Union[int, float]
            The current value of the metric to monitor.
        """
        logs = logs or {}
        monitor_value = logs.get(self.monitor)
        if monitor_value is None:
            logging.warning(
                f"Early stopping conditioned on metric '{self.monitor}' which is not available. Available metrics are: "
                f"{','.join(list(logs.keys()))}"
            )
        return monitor_value

    def _is_improvement(
        self, monitor_value: Union[int, float], reference_value: Union[int, float], **kwargs: dict
    ) -> bool:
        """Helper function to check if the target metric improved.

        Parameters
        ----------
        monitor_value : Union[int, float]
            The current value of the target metric.
        reference_value : Union[int, float]
            The best seen value of the target metric.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        bool
            ``True`` if an improvement was seen, ``False`` otherwise.
        """
        return self.monitor_op(monitor_value - self.min_delta, reference_value)

    def _is_overfit(self, logs: Optional[dict] = None, **kwargs: dict) -> bool:
        """Helper function to check if the overfitting is present, i.e. at least one overfitting condition returned ``True``.

        Parameters
        ----------
        logs : Optional[dict]
            Dictionary containing the metrics reported during training and validation. (Default value = None)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        bool
            ``True`` if overfitting was seen, ``False`` otherwise.
        """
        # go through all overfitting conditions and check is any of them is True
        is_overfit = False
        overfitting_reasons = []

        for condition_name, input_metric_names, condition in self.overfitting_conditions:
            input_values = [logs[input_name] for input_name in input_metric_names]
            if condition(*input_values):
                is_overfit = True
                overfitting_reasons.append(condition_name)

        return is_overfit, overfitting_reasons

    def calc_custom_metrics(self, logs: Optional[dict] = None, **kwargs: dict) -> dict:
        """Calculates the values of the `custom metrics` on the training and validation datasets.

        The predictions of the current model are calculated on the training and validation datasets. With the corresponding
        target labels, the values of the `custom metrics` can be determined. They are added to the ``logs``-dictionary with
        the name provided in ``self.custom_metrics`` and the prefix ``'train_'`` or ``'val_'``. The updated
        ``logs``-dictionary is returned.

        Parameters
        ----------
        logs : Optional[dict]
            Dictionary containing the metrics reported during training and validation. (Default value = None)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        dict
            Updated ``logs`` containing the values of the `custom metrics` on the training and validation datasets. The
            keys used correspond to the names provided in ``self.custom_metrics``, which the prefix ``'train_'`` or
            ``'val_'`` added for the values on the training and validation datasets, respectively.
        """
        if logs is None:
            logs = {}

        y_train_pred = self.predict(self.inputs_train, verbose=0, **kwargs)
        y_val_pred = self.predict(self.inputs_val, verbose=0, **kwargs)

        for metric_name, metric in self.custom_metrics:
            metric_value_train = metric(self.targets_train, y_train_pred, sample_weight=self.weights_train)
            metric_value_val = metric(self.targets_val, y_val_pred, sample_weight=self.weights_val)
            logs["train_" + metric_name] = metric_value_train
            logs["val_" + metric_name] = metric_value_val

        return logs

    def calc_composite_metrics(self, logs: dict, **kwargs: dict):
        """Calculates the values of the `composite metrics`.

        The names of the metrics used as inputs are expected to be present in the ``logs``-dictionary. The `composite metrics`
        are added to the ``logs``-dictionary using the names provided in ``self.composite_metrics``.

        Parameters
        ----------
        logs : dict
            Dictionary containing the metrics reported during training and validation.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        _type_
            Updated ``logs`` containing the values of the `composite metrics`. The keys used correspond to the names
            provided in ``self.composite_metrics``.
        """
        for metric_name, input_metric_names, metric in self.composite_metrics:
            input_values = [logs[input_name] for input_name in input_metric_names]
            metric_value = metric(*input_values)
            logs[metric_name] = metric_value

        return logs

    def build_results_dict(
        self,
        logs: dict,
        current_metrics: dict,
        current_weighted_metrics: dict,
        current_custom_metrics: dict,
        current_composite_metrics: dict,
        **kwargs: dict,
    ) -> dict:
        """Build the results dictionary from the current value of the target metric, `native`, `custom` and `composite metrics`.

        Additionally, all metrics that are needed to calculate the overtraining conditions are added to the results
        dictionary.

        In addition to the current values, the values corresponding to the best epoch so far are also added. The
        corresponding keys use the prefix ``'best_'``. Finally, the `last valid` value of the target metric, i.e. the
        value of the last epoch that passed all `overfitting conditions`, is added with the prefix ``'last_valid_'``.
        The early stopping status (``True`` if early stopping is triggered, ``False`` otherwise) is added with key
        ``'early_stopped'``.

        Parameters
        ----------
        logs : dict
            Dictionary containing the metrics reported during training and validation.
        current_metrics : dict
            Dictionary containing the current values of the `native metrics`.
        current_weighted_metrics : dict
            Dictionary containing the current values of the `weighted native metrics`.
        current_custom_metrics : dict
            Dictionary containing the current values of the `custom metrics`.
        current_composite_metrics : dict
            Dictionary containing the current values of the `composite metrics`.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        dict
            The results dictionary to be reported to `Tune`.
        """
        # get the current value of the metric to monitor
        monitor_value = self.get_monitor_value(logs, **kwargs)

        # build the results dictionary current, last valid and best value of the metric to optimize, the early stopping status,
        # the current and best values of all custom metrics and the current checkpoint
        results = {self.monitor: monitor_value, "early_stopped": self.early_stopped}
        results.update(current_metrics)
        results.update(current_weighted_metrics)
        results.update(current_custom_metrics)
        results.update(current_composite_metrics)
        results.update({f"best_{self.monitor}": self.best})
        results.update({f"best_{key}": value for key, value in self.best_metrics.items()})
        results.update({f"best_{key}": value for key, value in self.best_weighted_metrics.items()})
        results.update({f"best_{key}": value for key, value in self.best_custom_metrics.items()})
        results.update({f"best_{key}": value for key, value in self.best_composite_metrics.items()})
        results.update({f"last_valid_{self.monitor}": self.last_valid})

        # go though all the overtraining conditions and check if all required input metrics have been added to the results;
        # if not, add the missing metrics
        for _, metric_tuple, _ in self.overfitting_conditions:
            for metric in metric_tuple:
                if metric not in results.keys():
                    results[metric] = logs.get(metric)

        return results

    def finalize(self, **kwargs: dict):
        """Prints the final status message. This should be called at the end of the training.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        if self.wait >= self.patience_improvement and self.verbose > 0:
            print("Epoch {}: Early stopping...".format(self.stopped_epoch + 1))
        elif self.wait_overfitting >= self.patience_overfitting and self.verbose > 0:
            print("Epoch {}: Early stopping due to overfitting...".format(self.stopped_epoch + 1))

    state_type = tuple[int, int, int, Union[float, int], dict, dict, dict, dict, Any, int, int, bool, Union[float, int]]

    def get_state(self, **kwargs: dict) -> state_type:
        """Returns the values of all attributes needed to restore the state of the early stopper.

        This includes the number of epochs since the last improvement (``self.wait``), the number of epochs since the last
        time no `overfitting condition` was violated (``self.wait_overfitting``), the best target metric value seen
        (``self.best``), the dictionaries containing the values of the `native`, `weighted native`, `custom` and
        `composite metrics` after the best epoch (``self.best_metrics``, ``self.best_weighted_metrics``,
        ``self.best_custom_metrics`` and ``self.best_composite_metrics``), the model weights after the best epoch
        (``self.best_weights``), the best epoch (``self.best_epoch``), the epoch the optimization was early stopped on,
        a bool specifying if the optimization was early stopped and the value of the target metric after the last epoch
        that did not violate any `overfitting condition`.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        state_type
            The tuple containing all state variables.
        """
        return (
            self.current_epoch,
            self.wait,
            self.wait_overfitting,
            self.best,
            self.best_metrics,
            self.best_weighted_metrics,
            self.best_custom_metrics,
            self.best_composite_metrics,
            self.best_weights,
            self.best_epoch,
            self.stopped_epoch,
            self.early_stopped,
            self.last_valid,
        )

    def set_state(self, state: state_type, **kwargs: dict) -> None:
        """Restores the state of the early stopper.

        Parameters
        ----------
        state : state_type
            Early stopper state to restore from.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        (
            self.current_epoch,
            self.wait,
            self.wait_overfitting,
            self.best,
            self.best_metrics,
            self.best_weighted_metrics,
            self.best_custom_metrics,
            self.best_composite_metrics,
            self.best_weights,
            self.best_epoch,
            self.stopped_epoch,
            self.early_stopped,
            self.last_valid,
        ) = state

    def load_state(self, checkpoint_dir: str, **kwargs: dict) -> None:
        """Loads the early stopper state from the provided directory. 'early_stopper' is assumed to be the name of the pickle file.

        Parameters
        ----------
        checkpoint_dir : str
            Directory to load from.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        with open(os.path.join(checkpoint_dir, "early_stopper"), "rb") as f:
            self.set_state(pickle.load(f), **kwargs)

    def save_state(self, path: str, **kwargs: dict) -> None:
        """Saves the early stopper state to the provided path.

        Parameters
        ----------
        path : str
            Path to save the pickle-file to.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        with open(path, "wb") as f:
            pickle.dump(self.get_state(**kwargs), f)

    def copy_best_model(self, path: str, **kwargs: dict) -> None:
        """Copies the best model from the provided path to the ``self.checkpoint_dir`` directory.

        This is needed whenever the training is resumed from a checkpoint in order to copy the best model in the checkpoint
        to the working directory.

        Parameters
        ----------
        path : str
            Path of the best model in the checkpoint.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        try:
            shutil.copy2(path, self.checkpoint_dir)
        except shutil.SameFileError:
            pass

    @abstractmethod
    def get_train_val_metric_names(self, metric: str, **kwargs: dict) -> tuple[str, str]:
        """Returns the training and validation metric name to be used as the key in the ``logs`` dictionary.

        Parameters
        ----------
        metric : str
            _description_
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        tuple[str, str]
            The name of the metric on the training and validation dataset, as present in the ``logs`` dictionary.
        """

    @abstractmethod
    def get_weights(self, **kwargs: dict) -> Any:
        """Returns the current model weights.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        Any
            The current model weights.
        """
        raise NotImplementedError

    @abstractmethod
    def set_weights(self, weights: Any, **kwargs: dict) -> None:
        """Overwrites the current model weights with the provided weights.

        Parameters
        ----------
        weights : Any
            The model weights that should be applied.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        raise NotImplementedError

    @abstractmethod
    def save_model(self, output_dir: str, model_name: str, **kwargs: dict):
        """Saves the current model state into the provided directory.

        Parameters
        ----------
        output_dir : str
            Directory to save the model into.
        model_name : str
            The model name to use.
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        raise NotImplementedError

    @abstractmethod
    def predict(self, inputs: Any, verbose: int = 0, **kwargs: dict) -> np.ndarray:
        """Calculate the model predictions for the given inputs.

        Parameters
        ----------
        inputs : Any
            Data structure containing the input features.
        verbose : int
            Verbosity. Silent for  ``0``, prints messages for ``1``. (Default value = 0)
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.

        Returns
        -------
        np.ndarray
            Numpy array of the model predictions for the given input features.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_training(self, **kwargs: dict) -> None:
        """Mark the training for termination due to Early Stopping.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments that may be necessary for ML framework specific functionality, e.g. saving the
            model. They are provided to any call of a member function.
        """
        raise NotImplementedError


class CustomStopper(tune.Stopper):
    """Tune stopper that signifies the termination of a trial once the early stopper has set the ``'early_stopped'``-flag."""

    def __init__(self):
        """Constructor of CustomStopper."""
        self.should_stop = False

    def __call__(self, trial_id: Any, result: dict) -> bool:
        """Checks and returns the ``'early_stopped'``-flag of the provided results dictionary, thus terminating once early stopped.

        Parameters
        ----------
        trial_id : Any
            `Unused`.
        result : dict
            Results dictionary reported to `Tune` by an ``EarlyStopperForTuning``-instance.

        Returns
        -------
        bool
            Returns the ``'early_stopped'``-flag present in the results dictionary. If ``True``, the trial should be
            terminated.
        """
        # return True if the EarlyStopper said that the training should be stopped
        return result["early_stopped"]

    def stop_all(self) -> Literal[False]:
        """`Currently unused`.

        Returns
        -------
        Literal[False]
            Will currently always return ``False``.
        """
        # currently will always be false
        return self.should_stop


class PBTMutationHandler:
    """_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self) -> None:
        """_summary_.

        Returns
        -------
        None
            _description_
        """
        self._policies = None

    def load_experiment_state(self, experiment_dir: str) -> None:
        """_summary_.

        Parameters
        ----------
        experiment_dir : str
            _description_

        Returns
        -------
        None
            _description_
        """
        # collect the policies of all trials at the end of the optimization. This does not include any cut-off branches
        # where under-performing trials were overwritten during the optimization. These can be taken from the
        # pbt_global.txt file and will be handled in the future.
        # TODO: handle overwritten trials
        self._policies = {}
        for file in os.listdir(experiment_dir):
            if "pbt_policy_" in file:
                # strip the file name to get the trial
                trial = file.replace("pbt_policy_", "").replace(".txt", "")

                # extract the policy
                policy = self._load_policy(os.path.join(experiment_dir, file))

                # add the policy to the policies dict
                self._policies[trial] = policy

    def get_policy(self, trial: str) -> Optional[list[tuple[int, dict]]]:
        """_summary_.

        Parameters
        ----------
        trial : str
            _description_

        Returns
        -------
        Optional[list[tuple[int, dict]]]
            _description_
        """
        if self._policies is None:
            raise RuntimeWarning(
                "PBTMutation handler has not yet been initialized by loading an experiment via "
                "`load_experiment_state()` or loading a save state via `load()`."
            )
        return self._policies.get(trial)

    def save(self, savefile: str) -> None:
        """_summary_.

        Parameters
        ----------
        savefile : str
            _description_

        Returns
        -------
        None
            _description_
        """
        with open(savefile, "wb") as f:
            pickle.dump(self._policies, f)

    def load(self, savefile: str) -> None:
        """_summary_.

        Parameters
        ----------
        savefile : str
            _description_

        Returns
        -------
        None
            _description_
        """
        with open(savefile, "rb") as f:
            self._policies = pickle.load(f)

    def _load_policy(self, policy_file: str) -> list[tuple[int, dict]]:
        """_summary_.

        Parameters
        ----------
        policy_file : str
            _description_

        Returns
        -------
        list[tuple[int, dict]]
            _description_
        """
        raw_policy = []
        with open(policy_file, "rt") as fp:
            for row in fp.readlines():
                try:
                    parsed_row = json.loads(row)
                except json.JSONDecodeError:
                    raise ValueError("Could not read PBT policy file: {}.".format(policy_file)) from None
                raw_policy.append(tuple(parsed_row))

        # Loop through policy from end to start to obtain changepoints
        policy = []
        last_new_tag = None
        last_old_conf = None
        for old_tag, new_tag, _old_step, new_step, old_conf, new_conf in reversed(raw_policy):
            if last_new_tag and old_tag != last_new_tag:
                # Tag chain ended. This means that previous changes were
                # overwritten by the last change and should be ignored.
                break
            last_new_tag = new_tag
            last_old_conf = old_conf

            policy.append((new_step, new_conf))

        # Add the initial config to the policy
        policy.append((0, last_old_conf))

        # return the reversed list
        return list(reversed(policy))


def build_trainable(
    run_config: ModuleType,
    training_func: Callable,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    inputs_train: Union[np.ndarray, ray.ObjectRef],
    inputs_val: Union[np.ndarray, ray.ObjectRef],
    targets_train: Union[np.ndarray, ray.ObjectRef],
    targets_val: Union[np.ndarray, ray.ObjectRef],
    normalized_weights_train: Union[np.ndarray, ray.ObjectRef],
    normalized_weights_val: Union[np.ndarray, ray.ObjectRef],
    overtraining_conditions: Optional[list[tuple[str, str, Callable]]] = None,
    early_stopping_patience: Optional[int] = None,
    overtraining_patience: Optional[int] = None,
    num_threads: int = 1,
    create_checkpoints: bool = True,
    custom_metrics: Optional[list[tuple[str, Callable]]] = None,
    composite_metrics: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
    native_metrics: Optional[list] = None,
    weighted_native_metrics: Optional[list] = None,
    restore_best_weights: bool = False,
    run_in_subprocess: bool = True,
    verbose: int = 2,
) -> partial:
    """Puts the provided input data into `Ray`'s shared memory if needed and returns a ``functools.partial`` of the provided ``training_func``.

    Besides the arguments provided to this function, the ``training_func`` is expected to have the following arguments:

    - ``inputs_train``: ``ray.ObjectRef`` of ``inputs_train`` in `Ray`'s shared memory
    - ``inputs_val``: ``ray.ObjectRef`` of ``inputs_val`` in `Ray`'s shared memory
    - ``targets_train``: ``ray.ObjectRef`` of ``targets_train`` in `Ray`'s shared memory
    - ``targets_val``: ``ray.ObjectRef`` of ``targets_val`` in `Ray`'s shared memory
    - ``normalized_weights_train``: ``ray.ObjectRef`` of ``normalized_weights_train`` in `Ray`'s shared memory
    - ``normalized_weights_val``: ``ray.ObjectRef`` of ``normalized_weights_val`` in `Ray`'s shared memory
    - ``monitor``: Tuple containing the name of the target metric and either ``'min'`` or ``'max'`` to signify if this
      metric is to be minimized or maximized. This is set to ``(run_config.monitor_name, run_config.monitor_op)``.
    - ``overtraining_conditions``: the overfitting conditions provided in the run-config will be given unless
      ``overtraining_conditions`` is not ``None``, in which case ``overtraining_conditions`` is given.
    - ``early_stopping_patience``: will be populated with ``run_config.early_stopping_patience`` unless ``early_stopping_patience``
      is not ``None``, in which case ``early_stopping_patience`` is given.
    - ``overtraining_patience``: is populated with ``run_config.overtraining_patience`` unless ``overtraining_patience``
      is not ``None``, in which case ``overtraining_patience`` is given.
    - ``restore_on_best_checkpoint``: is populated with ``run_config.restore_on_best_checkpoint``

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    training_func : Callable
        Reference to the function used to train the `Keras` model.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``OPTIMA.builtin.inputs.InputHandler``-class
    inputs_train : Union[np.ndarray, ray.ObjectRef]
        Numpy array containing the input features of the training dataset.
    inputs_val : Union[np.ndarray, ray.ObjectRef]
        Numpy array containing the input features of the validation dataset.
    targets_train : Union[np.ndarray, ray.ObjectRef]
        Numpy array containing the target labels of the training dataset.
    targets_val : Union[np.ndarray, ray.ObjectRef]
        Numpy array containing the target labels of the validation dataset.
    normalized_weights_train : Union[np.ndarray, ray.ObjectRef]
        Numpy array containing the normalized event weights of the training dataset.
    normalized_weights_val : Union[np.ndarray, ray.ObjectRef]
        Numpy array containing the normalized event weights of the validation dataset.
    overtraining_conditions : Optional[list[tuple[str, str, Callable]]]
        List of `overfitting conditions`. (Default value = None)
    early_stopping_patience : Optional[int]
        Early stopping patience. (Default value = None)
    overtraining_patience : Optional[int]
        Patience before terminating due to overfitting. (Default value = None)
    num_threads : int
        Number of CPU threads used for the training of each model. (Default value = 1)
    create_checkpoints : bool
        Whether checkpoints of the current and best model and the early stopper state should be saved each epoch. (Default value = True)
    custom_metrics : Optional[list[tuple[str, Callable]]]
        List of `custom metrics`. (Default value = None)
    composite_metrics : Optional[list[tuple[str, tuple[str, str], Callable]]]
        List of `composite metrics`. (Default value = None)
    native_metrics : Optional[list]
        List of native metrics. (Default value = None)
    weighted_native_metrics : Optional[list]
        List of weighted native metrics. (Default value = None)
    restore_best_weights : bool
        Whether to restore the best weights after early stopping. (Default value = False)
    run_in_subprocess : bool
        Whether to execute the training in a subprocess. (Default value = True)
    verbose : int
        Verbosity mode. 0 = silent, 1 = progress bar, 2 = one line per epoch. Note that the progress bar is not
        particularly useful when logged to a file, so verbose=2 is recommended when not running interactively (e.g., in
        a production environment). (Default value = 2)

    Returns
    -------
    partial
        ``Partial`` of the ``training_func`` with the values of most arguments set.
    """
    # put large object in ray's shared memory
    if isinstance(inputs_train, np.ndarray):
        inputs_train = ray.put(inputs_train)
    if isinstance(inputs_val, np.ndarray):
        inputs_val = ray.put(inputs_val)
    if isinstance(targets_train, np.ndarray):
        targets_train = ray.put(targets_train)
    if isinstance(targets_val, np.ndarray):
        targets_val = ray.put(targets_val)
    if isinstance(normalized_weights_train, np.ndarray):
        normalized_weights_train = ray.put(normalized_weights_train)
    if isinstance(normalized_weights_val, np.ndarray):
        normalized_weights_val = ray.put(normalized_weights_val)

    # create the trainable that is executed by tuner.fit() (or e. g. during the cross validation). Use functools.partial here
    # instead of tune.with_parameters and add the numpy arrays to the object store manually because with tune.with_parameters,
    # the objects are never cleared from the object store again, thus consuming potentially large amounts of memory.
    # Note: in the past, using partial has caused problems with resuming an experiment. This has not yet been tested. TODO: test
    # TODO: when upgrading to Ray version >2.5.1, check if problem persists.
    trainable = partial(
        training_func,
        run_config=run_config,
        input_handler=input_handler,
        inputs_train=inputs_train,
        inputs_val=inputs_val,
        targets_train=targets_train,
        targets_val=targets_val,
        normalized_weights_train=normalized_weights_train,
        normalized_weights_val=normalized_weights_val,
        monitor=(run_config.monitor_name, run_config.monitor_op),
        custom_metrics=custom_metrics,
        composite_metrics=composite_metrics,
        native_metrics=native_metrics,
        weighted_native_metrics=weighted_native_metrics,
        overtraining_conditions=run_config.overtraining_conditions
        if overtraining_conditions is None
        else overtraining_conditions,
        early_stopping_patience=run_config.early_stopping_patience
        if early_stopping_patience is None
        else early_stopping_patience,
        overtraining_patience=run_config.overtraining_patience
        if overtraining_patience is None
        else overtraining_patience,
        restore_best_weights=restore_best_weights,
        restore_on_best_checkpoint=run_config.restore_on_best_checkpoint,
        num_threads=num_threads,
        create_checkpoints=create_checkpoints,
        run_in_subprocess=run_in_subprocess,
        verbose=verbose,
    )

    return trainable


def perform_crossvalidation(
    model_configs: list[model_config_type],
    model_output_dirs: list[str],
    training_func: Callable,
    run_config: ModuleType,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    cpus_per_model: int,
    gpus_per_model: int,
    custom_metrics: Optional[list[tuple[str, Callable]]] = None,
    composite_metrics: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
    native_metrics: Optional[list] = None,
    weighted_native_metrics: Optional[list] = None,
    return_futures: bool = False,
    verbose: int = 2,
    seed: Optional[int] = None,
) -> Union[tuple[dict, dict], tuple[dict, dict, list]]:
    """Performs k-fold crossvalidation for a given list of model-configs.

    The ``get_experiment_inputs``-function (either defined in the run-config or the built-in version ``OptimizationTools``) is
    called to load the input data for crossvalidation.

    For each fold, the trainable is build by calling ``build_trainable`` in order to save the datasets to Ray's shared
    memory (if needed) and to set constant arguments of the ``training_func``. The following choices are made:

    - ``run_config``: the provided ``run_config`` is passed.
    - ``training_func``: the provided ``training_func`` is wrapped with a ``ray.remote``-decorator, setting ``num_cpus``
      to ``cpus_per_model`` and ``num_gpus`` to ``gpus_per_model``, to allow remote execution of the trainable. The
      ``training_func`` needs to be decorated first before calling ``build_trainable`` as ``ray.remote`` does not accept
      ``functools.partial``.
    - ``inputs_train``, ``inputs_val``, ``targets_train``, ``targets_val``, ``normalized_weights_train`` and
      ``normalized_weights_val``: the corresponding arrays for each fold returned by ``get_experiment_inputs`` are passed.
    - ``overtraining_conditions``: default (``None``) if ``run_config.use_OT_conditions_for_crossvalidation`` is ``True``,
      ``[]`` otherwise. This disables the overfitting conditions during crossvalidation if necessary.
    - ``early_stopping_patience``: default (``None``) if ``run_config.use_early_stopping_for_crossvalidation`` is ``True``,
      ``run_config.max_epochs`` otherwise. This (effectively) disables early stopping during crossvalidation if necessary
      while still using the remaining functionality of the ``EarlyStopperForTuning``.
    - ``num_threads``: ``cpus_per_model`` is passed.
    - ``create_checkpoints``: ``True``.
    - ``custom_metrics``, ``composite_metrics``, ``native_metrics`` and ``weighted_native_metrics``: the corresponding
      arguments of this function are passed.
    - ``restore_best_weights``: ``True``. Since the best weights are only restored if the training is early stopped,
      this option can always be set to ``True``.
    - ``run_in_subprocess``: ``True``. This is done to ensure all resources reserved by Tensorflow are released when
      training terminates.
    - ``verbose``: ``verbose`` is passed.

    With the trainable and the datasets for all `k` folds ready, the training of the `k` models per provided model-config
    is started. While the number of epochs that were found to result in the best target metric by the
    ``evaluate_experiment`` is included in the ``model_config`` with the key ``'epochs'``, this is only used if
    ``run_config.use_early_stopping_for_crossvalidation`` is ``False``, in which case ``model_config["max_epochs"]``
    is overwritten with ``model_config["epochs"]``. For the model corresponding to the `i`-th fold, the output file name
    is set to `model_crossval_i` and path given in ``model_output_dirs[i]`` is used as the output directory. For each
    model, the presence of a `.crossvalidation_done`-file or a file with the target output name is checked. If any of the
    two files is present, the training for this model is skipped. The target output path is added to the model-config
    with key ``'final_model_path'``. The trainable is subsequently called, provided with the model-config, and the
    returned future (due to the remote execution) is saved to a list.

    If ``return_futures`` is ``False``, the function only returns once all trainings are terminated. To mark the
    crossvalidation as completed, a `.crossvalidation_done` file is created in each of the directories in
    ``model_output_dirs`` and the temporary directory ``'crossval_checkpoints'``containing the training checkpoints is
    removed. This allows the crossvalidation to be resumed if interruped at any point, and only the progress since the
    last model checkpoint is lost. If ``return_futures`` is ``True``, the list of ``futures`` is returned instead and
    the function does not block. The temporary checkpoint directory is subsequently not removed.

    Parameters
    ----------
    model_configs : list[model_config_type]
        A list of model configs for which crossvalidation should be performed.
    model_output_dirs : list[str]
        A list of paths to directories, one entry per config in ``model_configs``, to save the trained models in.
    training_func : Callable
        Reference to the function performing the training.
    run_config : ModuleType
        Reference to the imported run-config file.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``OPTIMA.builtin.inputs.InputHandler``-class
    cpus_per_model : int
        The number of CPUs to use to train each model.
    gpus_per_model : int
        The number of GPUs to use to train each model.
    custom_metrics : Optional[list[tuple[str, Callable]]]
        A list of `custom metrics` as defined in the run-config. (Default value = None)
    composite_metrics : Optional[list[tuple[str, tuple[str, str], Callable]]]
        A list of `composite metrics` as defined in the run-config. (Default value = None)
    native_metrics : Optional[list]
        A list of native metrics as defined in the run-config. (Default value = None)
    weighted_native_metrics : Optional[list]
        A list of weighted native metrics as defined in the run-config. (Default value = None)
    return_futures : bool
        If True, the list of futures given by `Ray` is returned instead of waiting for the workers to finish.
        (Default value = False)
    verbose : int
        Verbosity mode. 0 = silent, 1 = info messages and progress bar for training, 2 = info messages and one line per
        epoch. Note that the progress bar is not particularly useful when logged to a file, so verbose=2 is recommended
        when not running interactively (e.g., in a production environment). (Default value = 2)
    seed : Optional[int]
        If provided, the seed is used to set the numpy random state. Only used to generate a new seed for the model
        config if the original seed should not be reused. (Default value = None)

    Returns
    -------
    Union[tuple[dict, dict], tuple[dict, dict, list]]
        The first dictionary contains a list of dictionaries for each entry in ``model_output_dir``, which are used as
        keys. The inner dictionaries contain the output filename (key ``'name'``), which fold this model corresponds to
        (key ``'split'``) and the model-config used for the training, i.e. the corresponding entry in ``model_configs``,
        (key ``config``). Since one list entry is created for each trained model, the lists have length `k`. The second
        dictionary contains the training, validation and (if used) testing data used for each fold, with the number of
        each fold used as the key. The values are of the same form as the return values of ``get_experiment_inputs`` for
        ``inputs_for_crossvalidation = False``. If ``return_futures``, the list of futures of the remote workers are
        returned as well.
    """
    if weighted_native_metrics is None:
        weighted_native_metrics = []
    if native_metrics is None:
        native_metrics = []
    if composite_metrics is None:
        composite_metrics = []
    if custom_metrics is None:
        custom_metrics = []

    # set the random state (used only to generate a new random seed for the training if the old seed should not be reused)
    rng = np.random.RandomState(seed)

    # get the lists of input data
    if verbose > 0:
        print("Reloading the inputs for cross-validation...")
    if hasattr(run_config, "get_experiment_inputs"):
        get_experiment_inputs = run_config.get_experiment_inputs
    else:
        get_experiment_inputs = OPTIMA.core.inputs.get_experiment_inputs
    (
        inputs_split,
        targets_split,
        weights_split,
        normalized_weights_split,
    ) = get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True, disable_printing=verbose == 0)

    # simulate a @ray.remote() decorator on the training function
    training_func_remote = ray.remote(num_cpus=cpus_per_model, num_gpus=gpus_per_model)(training_func).remote

    # iterate over all input data splits, build the corresponding trainables, and add them to the list
    trainables_list = []
    crossval_input_data = (
        {}
    )  # save the split data and return it together with the names of the trained models for later evaluation
    for k, data_k in enumerate(zip(*inputs_split, *targets_split, *weights_split, *normalized_weights_split)):
        if run_config.use_testing_dataset:
            (
                inputs_train_k,
                inputs_val_k,
                inputs_test_k,
                targets_train_k,
                targets_val_k,
                targets_test_k,
                weights_train_k,
                weights_val_k,
                weights_test_k,
                normalized_weights_train_k,
                normalized_weights_val_k,
                normalized_weights_test_k,
            ) = data_k
            crossval_input_data[str(k)] = [
                [inputs_train_k, inputs_val_k, inputs_test_k],
                [targets_train_k, targets_val_k, targets_test_k],
                [weights_train_k, weights_val_k, weights_test_k],
                [normalized_weights_train_k, normalized_weights_val_k, normalized_weights_test_k],
            ]
        else:
            (
                inputs_train_k,
                inputs_val_k,
                targets_train_k,
                targets_val_k,
                weights_train_k,
                weights_val_k,
                normalized_weights_train_k,
                normalized_weights_val_k,
            ) = data_k
            crossval_input_data[str(k)] = [
                [inputs_train_k, inputs_val_k],
                [targets_train_k, targets_val_k],
                [weights_train_k, weights_val_k],
                [normalized_weights_train_k, normalized_weights_val_k],
            ]

        # build the trainable
        trainables_list.append(
            build_trainable(
                run_config,
                training_func_remote,
                input_handler,
                inputs_train_k,
                inputs_val_k,
                targets_train_k,
                targets_val_k,
                normalized_weights_train_k,
                normalized_weights_val_k,
                num_threads=cpus_per_model,
                create_checkpoints=True,
                custom_metrics=custom_metrics,
                composite_metrics=composite_metrics,
                native_metrics=native_metrics,
                weighted_native_metrics=weighted_native_metrics,
                early_stopping_patience=None
                if run_config.use_early_stopping_for_crossvalidation
                else run_config.max_epochs,  # effectively disables early stopping while keeping the custom metric and reporting functionality
                overtraining_conditions=None if run_config.use_OT_conditions_for_crossvalidation else [],
                restore_best_weights=True,
                run_in_subprocess=True,
                verbose=verbose,
            )
        )

    # make a copy of the configs since they are altered below
    model_configs = [config.copy() for config in model_configs]

    # iterate over all configs, for each config iterate over all trainables and append them and their args to the
    # callables_list
    futures = []
    crossval_model_info = {}
    if verbose > 0:
        print("Starting the training of the models.")
    for model_config, model_output_dir in zip(model_configs, model_output_dirs):
        # check if .crossvalidation_done file is present in the output directory; if yes, this means the crossvalidation
        # has already been done before and can be skipped
        skip_training = False
        if os.path.isfile(os.path.join(model_output_dir, ".crossvalidation_done")):
            if verbose > 0:
                print(
                    f".crossvalidation_done file found in {model_output_dir}, skipping the crossvalidation for this directory. "
                    f"If this is not intentional, delete the file at {os.path.join(model_output_dir, '.crossvalidation_done')} "
                    f"and all trained models that may be left and restart."
                )
            skip_training = True

        # get the number of epochs the optimization model was trained. When desired, set the maximum number of epochs to
        # the same value
        target_epochs = model_config["epochs"] if "epochs" in model_config.keys() else None
        if not run_config.use_early_stopping_for_crossvalidation and target_epochs is not None:
            model_config["max_epochs"] = target_epochs

        # if desired, overwrite the random seed with a fixed new value for all folds
        if not run_config.reuse_seed_for_crossvalidation and run_config.fixed_seed_for_crossvalidation:
            model_config["seed"] = rng.randint(*OPTIMA.core.tools.get_max_seeds())

        for k, trainable in enumerate(trainables_list):
            # if desired, overwrite the random seed with a new value for this fold
            model_config_k = model_config.copy()
            if not run_config.reuse_seed_for_crossvalidation and not run_config.fixed_seed_for_crossvalidation:
                model_config_k["seed"] = rng.randint(*OPTIMA.core.tools.get_max_seeds())

            output_name = f"model_crossval_{k}"
            output_path = os.path.join(model_output_dir, output_name)
            if model_output_dir not in crossval_model_info.keys():
                crossval_model_info[model_output_dir] = [
                    {"name": output_name, "split": str(k), "config": model_config_k}
                ]
            else:
                crossval_model_info[model_output_dir].append(
                    {"name": output_name, "split": str(k), "config": model_config_k}
                )
            if not skip_training:
                if OPTIMA.core.model.is_model(run_config, output_path):
                    if verbose > 0:
                        print(
                            f"The file {output_path} already exists. Assuming this is a fully trained model, not "
                            f"starting the training for this split..."
                        )
                else:
                    # adding the checkpoint directory and the final model path to the model's config, start the training
                    # and add the future to the list
                    model_config_k["checkpoint_dir"] = os.path.join(model_output_dir, "crossval_checkpoints", str(k))
                    model_config_k["final_model_path"] = output_path
                    futures.append(trainable(model_config_k))

    # this will block until all models are fully trained
    if return_futures:
        return crossval_model_info, crossval_input_data, futures
    else:
        ray.get(futures)

        # when crossvalidation is done, create all the .crossvalidation_done files and remove the temporary checkpoint directory
        for model_output_dir in model_output_dirs:
            open(os.path.join(model_output_dir, ".crossvalidation_done"), "w").close()
            shutil.rmtree(os.path.join(model_output_dir, "crossval_checkpoints"), ignore_errors=True)

        return crossval_model_info, crossval_input_data
