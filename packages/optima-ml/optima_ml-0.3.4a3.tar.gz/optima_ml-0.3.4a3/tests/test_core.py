# -*- coding: utf-8 -*-
"""Collection of unit tests core functionality."""
import os
import shutil
import pickle
import zipfile

import pytest

import numpy as np
import scipy
import functools

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # run tests on CPU
from ray import tune
import optuna

from .context import optima, evaluation, search_space, inputs, builtin_inputs, builtin_search_space
from . import config as run_config



def get_testing_search_space(optuna=False):
    run_config_search_space = {
        "fixed_int": 1,
        "fixed_float": 1.0,
        "fixed_str": "relu",
        "fixed_list": [1, 2, 3],
        "range_float": {
            "type": "range",
            "bounds": [1, 3],
            "supports_mutation": True,
        },
        "range_int": {
            "type": "range",
            "value_type": "int",
            "bounds": [100, 10000],
            "supports_mutation": True,
        },
        "range_float_quantized": {
            "type": "range",
            "bounds": [1, 3],
            "step": 0.02,
            "supports_mutation": True,
        },
        "range_int_quantized": {
            "type": "range",
            "value_type": "int",
            "bounds": [100, 10000],
            "step": 5,
            "supports_mutation": True,
        },
        "range_float_log": {
            "type": "range",
            "bounds": [1, 10000],
            "sampling": "log",
            "supports_mutation": True,
        },
        "range_int_log": {
            "type": "range",
            "value_type": "int",
            "bounds": [100, 10000],
            "sampling": "log",
            "supports_mutation": True,
        },
        "range_float_normal": {
            "type": "range",
            "sampling": "normal",
            "bounds": [-100, 100],
            "mean": 1,
            "std": 0.5,
            "supports_mutation": True,
        },
        "range_float_normal_quantized": {
            "type": "range",
            "sampling": "normal",
            "bounds": [-1000, 1000],
            "mean": 10,
            "std": 5,
            "step": 0.02,
            "supports_mutation": True,
        },
        "choice": {
            "type": "choice",
            "values": [1, 2, 3, 4],
            "supports_mutation": True,
        }
    }

    # optuna supports conditional and hierarchical search spaces, but does not support log quantization
    if optuna:
        run_config_search_space.update({
            "hierarchical_float_1": {
                "type": "range",
                "bounds": [1, 3],
                "only": (("range_float",), lambda range_float: range_float > 2)
            },
            "hierarchical_float_2": {
                "type": "range",
                "bounds": [1, 3],
                "only": (("hierarchical_float_1",), lambda hierarchical_float_1: hierarchical_float_1 is not None and hierarchical_float_1 > 2)
            },
            "conditional_float_1": {
                "type": "range",
                "bounds": (("range_float",), lambda range_float: [range_float, 3])
            },
            "conditional_float_2": {
                "type": "range",
                "bounds": (("conditional_float_1",), lambda conditional_float_1: [conditional_float_1, 3] if conditional_float_1 is not None else [1, 3])
            },
            "hierarchical_conditional_float_1": {
                "type": "range",
                "bounds": (("range_float",), lambda range_float: [range_float, 3]),
                "only": (("range_float",), lambda range_float: range_float > 2),
            },
            "hierarchical_conditional_float_2": {
                "type": "range",
                "bounds": (("hierarchical_conditional_float_1",), lambda hierarchical_conditional_float_1: [hierarchical_conditional_float_1, 3]),
                "only": (("hierarchical_conditional_float_1",), lambda hierarchical_conditional_float_1: hierarchical_conditional_float_1 is not None and hierarchical_conditional_float_1 > 2.5),
            }
        })
    else:
        run_config_search_space.update({
            "range_float_log_quantized": {
                "type": "range",
                "bounds": [1, 10000],
                "sampling": "log",
                "step": 0.02,
                "supports_mutation": True,
            },
            "range_int_log_quantized": {
                "type": "range",
                "value_type": "int",
                "bounds": [100, 100000],
                "sampling": "log",
                "step": 5,
                "supports_mutation": True,
            },
        })

    return run_config_search_space


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_build_tune_search_space():
    # get run-config style search space and convert to tune search space
    run_config_search_space = get_testing_search_space()
    tune_search_space = search_space.build_tune_search_space(run_config_search_space)

    # verify returned types
    assert isinstance(tune_search_space["fixed_int"], int)
    assert isinstance(tune_search_space["fixed_float"], float)
    assert isinstance(tune_search_space["fixed_str"], str)
    assert isinstance(tune_search_space["choice"], tune.search.sample.Categorical)
    assert isinstance(tune_search_space["range_float"], tune.search.sample.Float)
    assert isinstance(tune_search_space["range_int"], tune.search.sample.Integer)
    assert isinstance(tune_search_space["range_float_quantized"], tune.search.sample.Float)
    assert isinstance(tune_search_space["range_int_quantized"], tune.search.sample.Integer)
    assert isinstance(tune_search_space["range_float_log"], tune.search.sample.Float)
    assert isinstance(tune_search_space["range_int_log"], tune.search.sample.Integer)
    assert isinstance(tune_search_space["range_float_log_quantized"], tune.search.sample.Float)
    assert isinstance(tune_search_space["range_int_log_quantized"], tune.search.sample.Integer)
    assert isinstance(tune_search_space["range_float_normal"], tune.search.sample.Float)
    assert isinstance(tune_search_space["range_float_normal_quantized"], tune.search.sample.Float)

    # for non-categorical distributions, verify the distributions are correct
    uniform_float_samples = np.array([tune_search_space["range_float"].sample() for _ in range(10000)])
    uniform_int_samples = np.array([tune_search_space["range_int"].sample() for _ in range(10000)])
    uniform_float_step_samples = np.array([tune_search_space["range_float_quantized"].sample() for _ in range(10000)])
    uniform_int_step_samples = np.array([tune_search_space["range_int_quantized"].sample() for _ in range(10000)])
    log_float_samples = np.array([tune_search_space["range_float_log"].sample() for _ in range(10000)])
    log_int_samples = np.array([tune_search_space["range_int_log"].sample() for _ in range(10000)])
    log_float_step_samples = np.array([tune_search_space["range_float_log_quantized"].sample() for _ in range(10000)])
    log_int_step_samples = np.array([tune_search_space["range_int_log_quantized"].sample() for _ in range(10000)])
    normal_float_samples = np.array([tune_search_space["range_float_normal"].sample() for _ in range(10000)])
    normal_float_step_samples = np.array([tune_search_space["range_float_normal_quantized"].sample() for _ in range(10000)])

    assert scipy.stats.kstest(uniform_float_samples, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001  # uniform from loc to loc+scale
    assert scipy.stats.kstest(uniform_int_samples, scipy.stats.uniform(loc=100, scale=9900).cdf).pvalue > 0.001
    assert uniform_int_samples.dtype == "int64"
    assert scipy.stats.kstest(uniform_float_step_samples, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001
    assert (np.isclose(np.mod(uniform_float_step_samples, 0.02), 0) + np.isclose(np.mod(uniform_float_step_samples, 0.02), 0.02)).all()
    assert scipy.stats.kstest(uniform_int_step_samples, scipy.stats.uniform(loc=100, scale=9900).cdf).pvalue > 0.001
    assert uniform_int_step_samples.dtype == "int64"
    assert (np.isclose(np.mod(uniform_int_step_samples, 5), 0) + np.isclose(np.mod(uniform_int_step_samples, 5), 5)).all()
    assert scipy.stats.kstest(log_float_samples, scipy.stats.loguniform(1, 10000).cdf).pvalue > 0.001
    assert scipy.stats.kstest(log_int_samples, scipy.stats.loguniform(100, 10000).cdf).pvalue > 0.001
    assert log_int_samples.dtype == "int64"
    assert scipy.stats.kstest(log_float_step_samples, scipy.stats.loguniform(1, 10000).cdf).pvalue > 0.001
    assert (np.isclose(np.mod(log_float_step_samples, 0.02), 0) + np.isclose(np.mod(log_float_step_samples, 0.02), 0.02)).all()
    assert scipy.stats.kstest(log_int_step_samples, scipy.stats.loguniform(100, 100000).cdf).pvalue > 0.001
    assert log_int_step_samples.dtype == "int64"
    assert (np.isclose(np.mod(log_int_step_samples, 5), 0) + np.isclose(np.mod(log_int_step_samples, 5), 5)).all()
    assert scipy.stats.normaltest(normal_float_samples).pvalue > 0.001
    assert scipy.stats.normaltest(normal_float_step_samples).pvalue > 0.001
    assert (np.isclose(np.mod(normal_float_step_samples, 0.02), 0) + np.isclose(np.mod(normal_float_step_samples, 0.02), 0.02)).all()


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_optuna_search_space():  # TODO: implement conditional search space!
    # get run-config style search space
    run_config_search_space = get_testing_search_space(optuna=True)

    # build the optuna search space
    converted_search_space = functools.partial(search_space.optuna_search_space, search_space.serialize_conditions(run_config_search_space))

    # define a dummy objective
    def dummy_objective(trial):
        fixed_hps = converted_search_space(trial)
        return 1

    # perform the trial
    study = optuna.create_study(sampler=optuna.samplers.RandomSampler())
    study.optimize(dummy_objective, n_trials=10000)

    # get the trial parameters
    trial_params = [trial.params for trial in study.get_trials()]

    # # extract the suggested values for each hyperparameter
    uniform_float_samples = np.array([p["range_float"] for p in trial_params])
    uniform_int_samples = np.array([p["range_int"] for p in trial_params])
    uniform_float_step_samples = np.array([p["range_float_quantized"] for p in trial_params])
    uniform_int_step_samples = np.array([p["range_int_quantized"] for p in trial_params])
    log_float_samples = np.array([p["range_float_log"] for p in trial_params])
    log_int_samples = np.array([p["range_int_log"] for p in trial_params])

    # for normal values, use the "internal_" uniform values and transform to normal
    normal_float_samples = search_space._transform_uniform_to_normal(
        np.array([p["internal_range_float_normal"] for p in trial_params]),
        mean=1,
        std=0.5,
    )
    normal_float_step_samples = search_space._transform_uniform_to_normal(
        np.array([p["internal_range_float_normal_quantized"] for p in trial_params]),
        mean=1,
        std=0.5,
        step=0.02
    )

    # check distributions
    assert scipy.stats.kstest(uniform_float_samples, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001  # uniform from loc to loc+scale
    assert scipy.stats.kstest(uniform_int_samples, scipy.stats.uniform(loc=100, scale=9900).cdf).pvalue > 0.001
    assert uniform_int_samples.dtype == "int64"
    assert scipy.stats.kstest(uniform_float_step_samples, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.0001  # lower p-value due to discretization
    assert (np.isclose(np.mod(uniform_float_step_samples, 0.02), 0) + np.isclose(np.mod(uniform_float_step_samples, 0.02), 0.02)).all()
    assert scipy.stats.kstest(uniform_int_step_samples, scipy.stats.uniform(loc=100, scale=9900).cdf).pvalue > 0.001
    assert uniform_int_step_samples.dtype == "int64"
    assert (np.isclose(np.mod(uniform_int_step_samples, 5), 0) + np.isclose(np.mod(uniform_int_step_samples, 5), 5)).all()
    assert scipy.stats.kstest(log_float_samples, scipy.stats.loguniform(1, 10000).cdf).pvalue > 0.001
    assert scipy.stats.kstest(log_int_samples, scipy.stats.loguniform(100, 10000).cdf).pvalue > 0.001
    assert log_int_samples.dtype == "int64"
    assert scipy.stats.normaltest(normal_float_samples).pvalue > 0.001
    assert scipy.stats.normaltest(normal_float_step_samples).pvalue > 0.001
    assert (np.isclose(np.mod(normal_float_step_samples, 0.02), 0) + np.isclose(np.mod(normal_float_step_samples, 0.02), 0.02)).all()

    # grab the conditional and hierarchical hyperparameters. Since these will not always be present, set an impossible value
    # for the missing cases
    hierarchical_float_1_samples = np.array(
        [p["hierarchical_float_1"] if "hierarchical_float_1" in p.keys() else -100 for p in trial_params]
    )
    hierarchical_float_2_samples = np.array(
        [p["hierarchical_float_2"] if "hierarchical_float_2" in p.keys() else -100 for p in trial_params]
    )
    conditional_float_1_samples = np.array(
        [p["conditional_float_1"] if "conditional_float_1" in p.keys() else -100 for p in trial_params]
    )
    conditional_float_2_samples = np.array(
        [p["conditional_float_2"] if "conditional_float_2" in p.keys() else -100 for p in trial_params]
    )
    hierarchical_conditional_float_1_samples = np.array(
        [p["hierarchical_conditional_float_1"] if "hierarchical_conditional_float_1" in p.keys() else -100 for p in trial_params]
    )
    hierarchical_conditional_float_2_samples = np.array(
        [p["hierarchical_conditional_float_2"] if "hierarchical_conditional_float_2" in p.keys() else -100 for p in trial_params]
    )

    # start with the only hierarchical parameters. First check their hierarchy. To do that, replace all values in the 
    # samples where the condition is true with -100s, thus only -100s should be left 
    assert (np.where(uniform_float_samples > 2, -100, hierarchical_float_1_samples) == -100).all()
    assert (np.where(hierarchical_float_1_samples > 2, -100, hierarchical_float_2_samples) == -100).all()

    # Since their values do not depend on any other parameter, so we'd still expect a uniform distribution (except the -100s).
    assert scipy.stats.kstest(hierarchical_float_1_samples[hierarchical_float_1_samples != -100], scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001
    assert scipy.stats.kstest(hierarchical_float_2_samples[hierarchical_float_2_samples != -100], scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001

    # check the conditional hyperparameters. These should never be -100 (as they don't have a condition), but the
    # distribution should not be uniform anymore
    assert (conditional_float_1_samples != -100).all()
    assert scipy.stats.kstest(conditional_float_1_samples, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue < 0.001
    assert (conditional_float_2_samples != -100).all()
    assert scipy.stats.kstest(conditional_float_2_samples, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue < 0.001

    # we can recover the uniform distribution by remapping each samples range [uniform_float, 3] back to [1, 3]. First
    # calculate what fraction of the way from uniform_float to 3 the chosen value is: y = (x - uniform_float) / (3 - uniform_float),
    # and then choose the corresponding value in [1, 3]: 1 + (3 - 1) * y
    conditional_float_1_samples_remapped = 1 + (conditional_float_1_samples - uniform_float_samples) / (3 - uniform_float_samples) * (3 - 1)
    conditional_float_2_samples_remapped = 1 + (conditional_float_2_samples - conditional_float_1_samples) / (3 - conditional_float_1_samples) * (3 - 1)
    assert scipy.stats.kstest(conditional_float_1_samples_remapped, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001
    assert scipy.stats.kstest(conditional_float_2_samples_remapped, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001

    # now combine both for the hierarchical conditional values. We again test the hierarchy first.
    assert (np.where(uniform_float_samples > 2, -100, hierarchical_conditional_float_1_samples) == -100).all()
    assert (np.where(hierarchical_conditional_float_1_samples > 2.5, -100, hierarchical_conditional_float_2_samples) == -100).all()
    
    # now check the distributions, which should not be uniform, even without the -100s
    assert scipy.stats.kstest(hierarchical_conditional_float_1_samples[hierarchical_conditional_float_1_samples != -100], scipy.stats.uniform(loc=1, scale=2).cdf).pvalue < 0.001
    assert scipy.stats.kstest(hierarchical_conditional_float_2_samples[hierarchical_conditional_float_2_samples != -100], scipy.stats.uniform(loc=1, scale=2).cdf).pvalue < 0.001

    # but we can again recover this with a remapping
    hierarchical_conditional_float_1_samples_remapped = (
            1
            + (hierarchical_conditional_float_1_samples[uniform_float_samples > 2] - uniform_float_samples[uniform_float_samples > 2])
            / (3 - uniform_float_samples[uniform_float_samples > 2]) * (3 - 1)
    )
    hierarchical_conditional_float_2_samples_remapped = (
            1
            + (hierarchical_conditional_float_2_samples[hierarchical_conditional_float_1_samples > 2.5] - hierarchical_conditional_float_1_samples[hierarchical_conditional_float_1_samples > 2.5])
            / (3 - hierarchical_conditional_float_1_samples[hierarchical_conditional_float_1_samples > 2.5]) * (3 - 1)
    )
    assert scipy.stats.kstest(hierarchical_conditional_float_1_samples_remapped, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001
    assert scipy.stats.kstest(hierarchical_conditional_float_2_samples_remapped, scipy.stats.uniform(loc=1, scale=2).cdf).pvalue > 0.001


def test_prepare_search_space_for_PBT():
    # get run-config style search space
    run_config_search_space = get_testing_search_space(optuna=False)

    # start without a best_hp_values_optuna dict
    pbt_search_space_withFixed, pbt_search_space_mutatable = search_space.prepare_search_space_for_PBT(run_config_search_space)

    # verify returned types
    assert isinstance(pbt_search_space_withFixed["fixed_int"], int)
    assert isinstance(pbt_search_space_withFixed["fixed_float"], float)
    assert isinstance(pbt_search_space_withFixed["fixed_str"], str)
    assert isinstance(pbt_search_space_withFixed["choice"], tune.search.sample.Categorical)
    assert isinstance(pbt_search_space_withFixed["range_float"], tune.search.sample.Float)
    assert isinstance(pbt_search_space_withFixed["range_int"], tune.search.sample.Integer)
    assert isinstance(pbt_search_space_withFixed["range_float_quantized"], tune.search.sample.Float)
    assert isinstance(pbt_search_space_withFixed["range_int_quantized"], tune.search.sample.Integer)
    assert isinstance(pbt_search_space_withFixed["range_float_log"], tune.search.sample.Float)
    assert isinstance(pbt_search_space_withFixed["range_int_log"], tune.search.sample.Integer)
    assert isinstance(pbt_search_space_withFixed["range_float_log_quantized"], tune.search.sample.Float)
    assert isinstance(pbt_search_space_withFixed["range_int_log_quantized"], tune.search.sample.Integer)
    assert isinstance(pbt_search_space_withFixed["range_float_normal"], tune.search.sample.Float)
    assert isinstance(pbt_search_space_withFixed["range_float_normal_quantized"], tune.search.sample.Float)

    # verify that fixed values are not present in pbt_search_space_mutatable
    assert "fixed_int" in pbt_search_space_withFixed.keys()
    assert "fixed_float" in pbt_search_space_withFixed.keys()
    assert "fixed_str" in pbt_search_space_withFixed.keys()
    assert "fixed_int" not in pbt_search_space_mutatable.keys()
    assert "fixed_float" not in pbt_search_space_mutatable.keys()
    assert "fixed_str" not in pbt_search_space_mutatable.keys()

    # change range_float to non-mutatable and try again. we expect an AssertionError now
    run_config_search_space["range_float"]["supports_mutation"] = False
    try:
        pbt_search_space_withFixed, pbt_search_space_mutatable = search_space.prepare_search_space_for_PBT(run_config_search_space)
        raise AssertionError("expected an AssertionError to be raised, but it wasn't")
    except AssertionError:
        pass

    # now also provide a set of best hps
    best_hps = {}
    for hp in run_config_search_space.keys():
        if "fixed" in hp:
            best_hps[hp] = run_config_search_space[hp]
        else:
            best_hps[hp] = pbt_search_space_withFixed[hp].sample()
    pbt_search_space_withFixed, pbt_search_space_mutatable = search_space.prepare_search_space_for_PBT(
        run_config_search_space, best_hps
    )

    # range_float should now not be in mutatable anymore, and fixed to the best value
    assert "range_float" in pbt_search_space_withFixed.keys()
    assert "range_float" not in pbt_search_space_mutatable.keys()
    assert pbt_search_space_withFixed["range_float"] == best_hps["range_float"]


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_evaluate_experiment():  # TODO: add verification of plots?
    # get the necessary files from old evaluation; we need configs.pickle, dfs.pickle and analysis.pickle to perform the
    # evaluation
    if os.path.exists("tests/temp_test_evaluation"):
        shutil.rmtree("tests/temp_test_evaluation")
    if os.path.exists("tests/test_optimization"):
        shutil.rmtree("tests/test_optimization")
    with zipfile.ZipFile("tests/resources/test_optimization.zip", "r") as archive:
        archive.extractall("tests/temp_test_evaluation")
    os.makedirs("tests/temp_test_evaluation/optimization_evaluation/")
    shutil.copy2("tests/temp_test_evaluation/test_optimization/results/variable_optimization/configs.pickle", "tests/temp_test_evaluation/optimization_evaluation/configs.pickle")
    shutil.copy2("tests/temp_test_evaluation/test_optimization/results/variable_optimization/dfs.pickle", "tests/temp_test_evaluation/optimization_evaluation/dfs.pickle")
    with open("tests/temp_test_evaluation/test_optimization/results/variable_optimization/analysis.pickle", "rb") as file:
        analysis = pickle.load(file)

    # do necessary setup for evaluation
    input_handler = builtin_inputs.InputHandler(run_config)
    (inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = inputs.get_experiment_inputs(run_config, input_handler, output_dir=None)

    # get metrics
    custom_metrics = run_config.custom_metrics
    composite_metrics = run_config.composite_metrics
    native_metrics = run_config.native_metrics
    weighted_native_metrics = run_config.weighted_native_metrics

    # get the search space and add a few entries
    run_config.search_space["max_epochs"] = run_config.max_epochs
    run_config.search_space["first_checkpoint_epoch"] = run_config.checkpoint_frequency
    run_config.search_space["checkpoint_frequency"] = run_config.checkpoint_frequency

    # evaluation; get the raw metric values to compare
    best_trials_test, best_trials_fit_test, configs_df_test, _, raw_metric_values_test = \
        evaluation.evaluate_experiment(analysis,
                                       optima.train_model,
                                       run_config,
                                       run_config.monitor_name,
                                       run_config.monitor_op,
                                       run_config.search_space,
                                         "tests/temp_test_evaluation/optimization_evaluation",
                                       inputs_split,
                                       targets_split,
                                       weights_split,
                                       normalized_weights_split,
                                       input_handler,
                                       custom_metrics=custom_metrics,
                                       composite_metrics=composite_metrics,
                                       native_metrics=native_metrics,
                                       weighted_native_metrics=weighted_native_metrics,
                                       cpus_per_model=1,
                                       gpus_per_model=0,
                                       overtraining_conditions=run_config.overtraining_conditions,
                                       return_results_str=True,
                                       return_unfilled=True)

    # get the results of the previous evaluation
    with open("tests/temp_test_evaluation/optimization_evaluation/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials,
            best_trials_fit,
            configs_df,
            _,
            _,
            _,
            _,
            _,
            _,
            evaluation_string,
            raw_metric_values
        ) = pickle.load(evaluation_file)

    # we assume that the results of the optimization are identical, and the results of the evaluation are close (but need
    # not be identical due to numerical differences on different systems arising during the crossvalidation)
    assert best_trials.equals(best_trials_test)
    assert best_trials_fit.equals(best_trials_fit_test)
    assert configs_df.equals(configs_df_test)
    for raw, raw_test in zip(raw_metric_values, raw_metric_values_test):
        if raw != 0 or raw_test != 0:
            assert abs(2 * (raw - raw_test) / (raw + raw_test)) < 1e-3

    # cleanup
    shutil.rmtree("tests/temp_test_evaluation")
