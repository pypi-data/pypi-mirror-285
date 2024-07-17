# -*- coding: utf-8 -*-
"""A module that provides functions to handle the search space for the hyperparameter optimization for the build-in multilayer perceptrons."""
from OPTIMA.core.model import model_config_type


def get_hp_defaults() -> tuple[model_config_type, model_config_type]:
    """Provides default values for all hyperparameters needed by the built-in ``build_model`` and ``compile_model``-functions.

    This function is specific to the built-in ``build_model`` and ``compile_model``-functions for classification using
    multilayer perceptrons. If they are not overwritten, hyperparameters that are omitted from the search space will be
    set to their default values. When defining an own ``build_model`` or ``compile_model``-function, this functionality
    is disabled and the corresponding default values will NOT be added to the search space, thus all necessary
    hyperparameter are expected to be present in the search space.

    Returns
    -------
    tuple[model_config_type, model_config_type]
        Dictionaries with the names of all hyperparameters as keys and the corresponding default values as values. The
        first return value contains the hyperparameters of the built-in ``build_model``-function, the second return value
        the hyperparameters of the built-in ``compile_model``-function.
    """
    hyperparameter_defaults_build = {
        "num_layers": 3,
        "units": 32,
        "activation": "swish",
        "kernel_initializer": "auto",
        "bias_initializer": "auto",
        "l1_lambda": 0.0,
        "l2_lambda": 0.0,
        "dropout": 0.1,
        "batch_size": 64,
    }
    hyperparameter_defaults_compile = {
        "learning_rate": 0.001,
        "Adam_beta_1": 0.9,
        "one_minus_Adam_beta_2": 0.001,
        "Adam_epsilon": 1e-7,
        "loss_function": "BinaryCrossentropy",
    }
    return hyperparameter_defaults_build, hyperparameter_defaults_compile


def get_hps_to_mutate() -> tuple[list[str], list[str]]:
    """Provides a list of built-in hyperparameters that allow mutation.

    This function is specific to the built-in ``build_model`` and ``compile_model``-functions. If either of the two
    functions are overwritten, the corresponding hyperparameters are not assumed to be mutatable anymore.

    Returns
    -------
    tuple[list[str], list[str]]
        Two lists of mutatable, built-in hyperparameters. The first return value contains the mutatable hyperparameters
        of the built-in ``build_model``-function, the second return value the hyperparameters of the built-in
        ``compile_model``-function.
    """
    mutatable_hps_build = ["l1_lambda", "l2_lambda", "dropout", "batch_size"]
    mutatable_hps_compile = ["learning_rate", "Adam_beta_1", "one_minus_Adam_beta_2", "Adam_epsilon"]
    return mutatable_hps_build, mutatable_hps_compile
