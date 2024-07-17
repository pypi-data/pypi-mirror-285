# -*- coding: utf-8 -*-
"""A module that provides general functionality to handle the hyperparameter search space."""
from typing import Union, Optional, Callable, Any, Literal

import numpy as np
import scipy
import dill

import optuna
from ray import tune

import OPTIMA.core.tools

run_config_search_space_entry_type = Union[int, float, str, list, tuple, dict]

tune_search_space_entry_type = Union[
    tune.search.sample.Float,
    tune.search.sample.Integer,
    tune.search.sample.Categorical,
    list,
    dict,
    str,
    float,
    int,
]
tune_search_space_type = dict[
    str,
    tune_search_space_entry_type,
]

PBT_search_space_type = dict[
    str, Union[tune.search.sample.Float, tune.search.sample.Integer, tune.search.sample.Categorical, list, dict]
]


def _get_range_search_space_properties(
    hp_name: str, hp_value: dict, optuna: bool = False
) -> tuple[
    list, str, str, Union[int, float, Literal[None]], Union[int, float, Literal[None]], Union[int, float, Literal[None]]
]:
    """Helper function to extract relevant information from a ``'range'`` search space entry in the run-config format.

    This function enforces the following conditions:

    - a ``'bounds'`` entry is provided as a list of length two, with ``bounds[0] <= bounds[1]``
    - a ``'value_type'`` entry can only have values ``'int'`` and ``'float'``
    - a ``'value_type'`` entry can only have values ``'uniform'``, ``'log'`` and ``'normal'``
    - for integer search spaces, the ``'step'`` value must be an integer (or an integer represented as a float, e.g. ``2.0``)
    - for integer search spaces with log sampling, ``'step'`` can only be 1 when using Optuna
    - ``'mean'`` and ``'std'`` need to be provided for normal-sampled search spaces
    - normal sampled integer search spaces are not supported

    The following default values are set for vacant search space entries:

    - ``'value_type'``: ``'float'``
    - ``'sampling'``: ``'uniform'``
    - ``'step'``: ``None``

    Parameters
    ----------
    hp_name : str
        Name of the ``'range'`` hyperparameter in the search space.
    hp_value : dict
        Corresponding search space entry.
    optuna : bool
        Indicates if Optuna is used for the hyperparameter optimization. (Default value = False)

    Returns
    -------
    tuple[list, str, str, Union[int, float, Literal[None]], Union[int, float, Literal[None]], Union[int, float, Literal[None]]]
        A list containing the lower and upper bounds of the hyperparameter, either ``'int'`` or ``'float'`` describing
        the type of hyperparameter value, a string describing the desired sampling of the search space (``'uniform'``,
        ``'log'`` or ``'normal'``), and optional step size for quantization (``None`` if unquantized), an optional mean
        and standard deviation values for ``'normal'`` search spaces (both ``None`` for other samplings).
    """
    assert "bounds" in hp_value.keys(), "Bounds need to be provided for search space entry of type 'range'!"
    bounds = hp_value["bounds"]

    # gather properties of this search space entry and set defaults for vacant entries
    if hp_value.get("value_type") is not None:
        assert hp_value["value_type"] in [
            "int",
            "float",
        ], f"Unsupported value type {hp_value['value_type']} for hyperparameter {hp_name}."
        value_type = hp_value["value_type"]
    else:
        value_type = "float"
    if hp_value.get("sampling") is not None:
        assert hp_value["sampling"] in [
            "uniform",
            "log",
            "normal",
        ], f"Unsupported sampling option {hp_value['sampling']} for hyperparameter {hp_name}."
        sampling = hp_value["sampling"]
    else:
        sampling = "uniform"
    if hp_value.get("step") is not None:
        if value_type == "int" and int(hp_value["step"]) != hp_value["step"]:
            raise ValueError(
                f"A step value of {hp_value['step']} is not possible for integer search space of {hp_name}!"
            )
        if sampling == "log" and optuna:
            raise ValueError(
                "Optuna does not support discrete log sampling. Set step to None or sampling to 'uniform'."
            )
        step = hp_value["step"]
    else:
        step = None
    if sampling == "normal":
        if value_type == "int":
            raise ValueError(f"Integer normal search space of {hp_name} is not supported by Tune!")
        assert (
            "mean" in hp_value.keys() and "std" in hp_value.keys()
        ), f"'mean' and 'std' must be provided for 'normal' search space of {hp_name}."
        mean = hp_value["mean"]
        std = hp_value["std"]
    else:
        mean, std = None, None

    return bounds, value_type, sampling, step, mean, std


def _build_search_space_properties(hp_name: str, hp_value: dict, optuna: bool = False) -> tuple[str, tuple]:
    """Helper function to extract relevant information from a search space entry in the run-config format.

    If the search space value is not a dictionary, the hyperparameter is considered fixed to the provided value and
    returned, together with the search space type ``'fixed'``. Otherwise, a distinction is made between ``'range'``
    and ``'choice'`` parameters. For ``'range'`` parameters, the ``_get_range_search_space_properties``-function is
    called to retrieve relevant information. The obtained properties are returned together with the search space type
    ``'range'``. For ``'choice'``-parameters, a ``'values'``-entry is asserted to be present in the search space entry,
    which is returned together with the search space type ``'choice'``.

    Since the ``'bounds'`` entry is only used for ``'range'``-parameters and the ``'values'``-entry is only used for
    choice parameters, the presence of these entries is also used to infer if the search space type is ``'range'`` or
    ``'choice'``, thus making the ``'type'`` entry optional.

    Parameters
    ----------
    hp_name : str
        Name of the ``'range'`` hyperparameter in the search space.
    hp_value : dict
        Corresponding search space entry.
    optuna : bool
        Indicates if Optuna is used for the hyperparameter optimization. (Default value = False)

    Returns
    -------
    tuple[str, tuple]
        The first return value describes the type of search space, either ``'fixed'``, ``'range'`` or ``'choice'``. The
        second return value is a tuple of all relevant information. For a fixed hyperparameter, this is the value set
        in the run-config. For a choice parameter, this is the value provided as ``'values'``. For a range parameter,
        this is a tuple containing a list with the lower and upper bounds of the hyperparameter, either ``'int'`` or
        ``'float'`` describing the type of hyperparameter value, a string describing the desired sampling of the search
        space (``'uniform'``, ``'log'`` or ``'normal'``), an optional step size for quantization (``None`` if
        unquantized), and optional mean and standard deviation values for ``'normal'`` search spaces (both ``None``
        for other samplings).
    """
    # first check if hyperparameter is fixed
    if not isinstance(hp_value, dict):
        search_space_type = "fixed"
        search_space_entry = hp_value
    else:
        # check if it is a range or choice parameter; this can be given via the "type" option or inferred from the
        # presence of the "bounds" or "values" option
        if hp_value.get("type") == "range" or "bounds" in hp_value.keys():
            # get the properties of this search space entry and set default values for vacant entries
            search_space_type = "range"
            bounds, value_type, sampling, step, mean, std = _get_range_search_space_properties(
                hp_name, hp_value, optuna=optuna
            )
            search_space_entry = (bounds, value_type, sampling, step, mean, std)
        elif hp_value.get("type") == "choice" or "values" in hp_value.keys():
            assert "values" in hp_value.keys(), "Values must be provided for choice search space!"
            search_space_type = "choice"
            search_space_entry = hp_value["values"]
        else:
            raise ValueError(f"Unsupported search space type for hyperparameter {hp_name}: {hp_value}")

    return search_space_type, search_space_entry


def serialize_conditions(
    search_space: dict[str, run_config_search_space_entry_type]
) -> dict[str, run_config_search_space_entry_type]:
    """A helper function that serializes all callables in the search space to a string representation.

    Since the search space needs to be serializable with ``pickle``, it must not contain any callables. However, since
    conditions are described via callables in the run-config, these need to be explicitly serialized beforehand.

    Callables, i.e. conditions, are only expected as the second arguments of the ``'bounds'``, ``'values'`` and ``'only'``
    entries for each search space entry. If a callable is detected, it is translated into a bytestring using
    ``dill.dumps()``, and added to the search space in place of the callable. When suggesting hyperparameters, this
    representation can be translated back into the original callable to evaluate the condition.

    This function does not alter the original provided search space. Instead, it returns a copy with the callables
    replaced by their bytestring representations.

    Parameters
    ----------
    search_space : dict[str, run_config_search_space_entry_type]
        The search space in the run-config format.

    Returns
    -------
    dict[str, run_config_search_space_entry_type]
        A copy of the provided search space, with the callables replaced by their bytestring representations obtained
        using ``dill.dumps()``.
    """
    serialized_search_space = search_space.copy()
    for hp_name, hp_value in search_space.items():
        if isinstance(hp_value, dict):
            serialized_hp_value = hp_value.copy()
            if "bounds" in hp_value.keys() and callable(hp_value["bounds"][1]):
                bounds_hps, bounds_callable = hp_value["bounds"]
                serialized_hp_value["bounds"] = (bounds_hps, dill.dumps(bounds_callable))
            if "values" in hp_value.keys() and callable(hp_value["values"][1]):
                values_hps, values_callable = hp_value["values"]
                serialized_hp_value["values"] = (values_hps, dill.dumps(values_callable))
            if "only" in hp_value.keys():
                only_hps, only_callable = hp_value["only"]
                serialized_hp_value["only"] = (only_hps, dill.dumps(only_callable))
            serialized_search_space[hp_name] = serialized_hp_value
    return serialized_search_space


def build_tune_search_space(
    search_space: dict[str, run_config_search_space_entry_type],
    PBT: Optional[bool] = False,
) -> tune_search_space_type:
    """Translates the search space format from the run-config to a Tune search space.

    Since Tune does not support conditional search spaces, a ``ValueError`` will be raised if a conditional search space
    is provided.

    Parameters
    ----------
    search_space : dict[str, run_config_search_space_entry_type]
        The search space in the format used in the run-config.
    PBT : Optional[bool]
        Since Population Based Training expects lists instead of a tune.search.sample.Categorical-instance, will not
        convert search space entries of type ``'choice'``. Instead, the ``'values'``-entry is returned directly.
        (Default value = False)

    Returns
    -------
    tune_search_space_type
        The search space to be provided to Tune.
    """
    # verify the search space is not conditional
    for _, hp_value in search_space.items():
        if isinstance(hp_value, dict):
            is_conditional = False
            if "only" in hp_value.keys():
                is_conditional = True
            elif "bounds" in hp_value.keys() and callable(hp_value["bounds"][1]):
                is_conditional = True
            elif "values" in hp_value.keys() and callable(hp_value["values"][1]):
                is_conditional = True
            if is_conditional:
                raise ValueError("Tune does not support conditional search spaces!")

    # build the tune search space
    tune_search_space = {}
    for hp_name, hp_value in search_space.items():
        # get the search space properties, i.e. a set of options that are needed to specify the search space entry.
        # Vacant options are populated with default values
        search_space_type, search_space_properties = _build_search_space_properties(hp_name, hp_value)

        # choose the correct Tune search space
        if search_space_type == "fixed":
            tune_search_space[hp_name] = search_space_properties
        elif search_space_type == "range":
            bounds, value_type, sampling, step, mean, std = search_space_properties
            if value_type == "float" and sampling == "uniform" and step is None:
                tune_search_space[hp_name] = tune.uniform(bounds[0], bounds[1])
            elif value_type == "float" and sampling == "uniform" and step is not None:
                tune_search_space[hp_name] = tune.quniform(bounds[0], bounds[1], step)
            elif value_type == "float" and sampling == "log" and step is None:
                tune_search_space[hp_name] = tune.loguniform(bounds[0], bounds[1])
            elif value_type == "float" and sampling == "log" and step is not None:
                tune_search_space[hp_name] = tune.qloguniform(bounds[0], bounds[1], step)
            elif sampling == "normal" and step is None:
                tune_search_space[hp_name] = tune.randn(mean, std)
            elif sampling == "normal" and step is not None:
                tune_search_space[hp_name] = tune.qrandn(mean, std, step)
            elif value_type == "int" and sampling == "uniform" and step is None:
                tune_search_space[hp_name] = tune.randint(bounds[0], bounds[1] + 1)  # upper bound is exclusive
            elif value_type == "int" and sampling == "uniform" and step is not None:
                if step != 1:
                    tune_search_space[hp_name] = tune.qrandint(
                        bounds[0], bounds[1], step
                    )  # upper bound is inclusive if step != 1
                else:
                    tune_search_space[hp_name] = tune.randint(bounds[0], bounds[1] + 1)
            elif value_type == "int" and sampling == "log" and step is None:
                tune_search_space[hp_name] = tune.lograndint(bounds[0], bounds[1] + 1)  # upper bound is exclusive
            elif value_type == "int" and sampling == "log" and step is not None:
                if step != 1:
                    tune_search_space[hp_name] = tune.qlograndint(
                        bounds[0], bounds[1], step
                    )  # upper bound is inclusive if step != 1
                else:
                    tune_search_space[hp_name] = tune.lograndint(bounds[0], bounds[1] + 1)
        elif search_space_type == "choice":
            if PBT:
                tune_search_space[hp_name] = list(search_space_properties)
            else:
                tune_search_space[hp_name] = tune.choice(search_space_properties)
        else:
            raise RuntimeError(f"Unknown search space type {search_space_type}.")

    return tune_search_space


def _transform_uniform_to_normal(
    x: Union[int, float], mean: Union[int, float], std: Union[int, float], step: Optional[Union[int, float]] = None
) -> float:
    """Helper function to transform a uniformly distributed to a normally distributed random variable with provided mean and width.

    The relationship between the two distributions is given by the Gaussian probability point function. The calculation
    is done using Scipy's ``scipy.stats.norm.ppf``.

    The result is optionally quantized to the nearest multiple of ``step``.

    Parameters
    ----------
    x : Union[int, float]
        The uniformly distributed random variable to transform to a normal.
    mean : Union[int, float]
        The mean of the normal distribution.
    std : Union[int, float]
        The standard deviation of the normal distribution.
    step : Optional[Union[int, float]]
        An optional step size to use for quantization. (Default value = None)

    Returns
    -------
    float
        The corresponding value of the normally distributed random variable.
    """
    y = scipy.stats.norm.ppf(x, loc=mean, scale=std)
    if step is not None:
        y = np.round(y / step) * step  # round to nearest multiple of step
    return y


def _optuna_suggest_normal(
    trial: optuna.trial.Trial,
    hp_name: str,
    mean: Union[int, float],
    std: Union[int, float],
    step: Optional[Union[int, float]] = None,
) -> float:
    """Helper function to suggest a normally distributed variable with Optuna.

    Since Optuna does not natively support normal distributions, we instead need to sample from a uniform distribution
    and transform the value using the inverse CDF, i.e. the probability point function, to get from a quantile to the
    corresponding value.

    If a step size is provided resulting value is quantized by rounding to the nearest multiple of ``step``.

    As a side-effect of the uniform suggestion, a new hyperparameter will be added to the trial. As the name, the
    provided hyperparameter name with an ``'internal_'`` prefix is used to distinguish this hyperparameter from the
    others.

    Parameters
    ----------
    trial : optuna.trial.Trial
        The Optuna trial for which a normally distributed hyperparameter value should be suggested.
    hp_name : str
        The name of the hyperparameter.
    mean : Union[int, float]
        The mean of the normal distribution.
    std : Union[int, float]
        The standard deviation of the normal distribution.
    step : Optional[Union[int, float]]
        An optional step size to use for quantization. (Default value = None)

    Returns
    -------
    float
        The value of the normally distributed hyperparameter.
    """
    temp_uniform = None
    while temp_uniform is None or temp_uniform == 0 or temp_uniform == 1:  # make sure 0 and 1 are excluded!
        temp_uniform = trial.suggest_float(f"internal_{hp_name}", 0, 1)
    y_normal = _transform_uniform_to_normal(temp_uniform, mean, std, step)

    return y_normal


def optuna_search_space(search_space: dict[str, run_config_search_space_entry_type], trial: optuna.trial.Trial) -> dict:
    """Suggests new hyperparameters using Optuna's define-by-run API for serialized conditional search spaces in the run-config format.

    This function supports conditional hyperparameter bounds for range parameters and conditional values for choice
    parameters, allowing to constrain the possible values of a hyperparameter based on other hyperparameter values.
    Additionally, hierarchical search spaces can be build using the ``'only'`` value, allowing a hyperparameter to only
    be suggested if a condition is fulfilled.

    Since this function needs to be serializable, the conditions in the provided search space are expected to be converted
    to their bytestring representations using ``dill``. As such, a value of type ``bytes`` as the second entry of a
    ``'bounds'`` or ``'values'`` entry is interpreted as an encoded callable.

    Since hyperparameters are not independent anymore for conditional and hierarchical search spaces, the order of the
    hyperparameter suggestions matters. In particular, while the final set of suggested hyperparameters does not depend
    on the order they were suggested, the conditions prevent certain orders from being evaluable. As an example, if
    values for three hyperparameters `a`, `b` and `c` are to be suggested, where `a` and `b` depend on the value of `c`,
    allowed orders of evaluation are `c`, `a`, `b` and `c`, `b`, `a`. Since `a` and `b` are independent with respect to
    each other, their respective order does not influence the suggested values. Any other order, however, is obviously
    forbidden.

    To solve the conditional, hierarchical hyperparameter space, the following order is used:

    1. Suggest values for all non-conditional hyperparameters. These are hyperparameters whose search space does not
       contain an ``'only'``-entry and whose ``'bounds'`` or ``'values'`` entry (if present) is not conditional.
    2. In an arbitrary order, iterate over the remaining hyperparameters and check if the hyperparameter's
       ``'only'``-condition is evaluable (i.e. values have been suggested for all hyperparameters that the
       ``'only'``-condition depends on). If this is not the case, continue to the next remaining hyperparameter. If the
       ``'only'``-condition is evaluable, evaluate it. If it returns as ``False``, i.e. this hyperparameter is not needed,
       remove it from the list of remaining hyperparameters and continue to the next remaining hyperparameter. If a
       hyperparameter does not have an ``'only'``-condition, it is considered to be ``True``. If the ``'only'``-condition
       is ``True``, check if this hyperparameter's conditional ``'bounds'`` or ``'values'`` can be evaluated.  If this is
       not the case, continue to the next remaining hyperparameter. If a hyperparameter does not have conditional
       ``'bounds'`` or ``'values'``, they are (of cause) considered evaluable. Finally, suggest a value for this
       hyperparameter and continue to the next remaining hyperparameter.
    3. Iteratively repeat step 2 until a value has been suggested for all hyperparameters. If no new hyperparameter value
       is suggested during an iteration, this indicates a circular condition which is not resolvable, and a ``ValueError``
       is raised.

    An additional layer of complexity arises if hyperparameters depend on hyperparameters with an ``'only'``-condition.
    As an example, assume hyperparameter B depends on hyperparameter A with the ``'only'``-condition ``A > 0.5``, and
    hyperparameter C depends on B with the ``'only'``-condition ``B > 0.5``. For the suggestion ``A = 0``, the value of
    B is undefined, thus C's ``'only'``-condition cannot be evaluated. The same situation arises if the value of C depends
    on the value of B. To let the user decide on how to deal with such a scenario, the value of a hyperparameter
    whose ``'only'``-condition was evaluated as ``False`` is set to ``None``, so that it can be provided to the other
    hyperparameter's conditions. In the example, the ``'only'``-condition of C could for example be adjusted to
    ``B is not None and B > 0.5`` or ``B is None or B > 0.5``, depending on the intentions. Similarly, if the value of
    C depends on the value of B, one could either define a default range like ``[B, 3] if B is not None else [0, 3]`` or
    add an ``'only'``-condition ``B is not None``.

    Parameters
    ----------
    search_space : dict[str, run_config_search_space_entry_type]
        The search space in the run-config format, with callables represented as bytestrings.
    trial : optuna.trial.Trial
        The Optuna trial for which hyperparameters should be suggested.

    Returns
    -------
    dict
        A dictionary of fixed hyperparameters. This is expected by Optuna's define-by-run API.
    """
    # split search space entries into conditional and non-conditional entries and extract the search space properties
    conditional_search_space = {}
    non_conditional_search_space = {}
    for hp_name, serialized_hp_value in search_space.items():
        # assign to conditional and non-conditional sub-search space dicts; serialized callables are bytes instances
        # collect a list of hyperparameters that is needed to check if hp is necessary, and a second list of hps that is
        # needed to decide on a value
        only_depends_hps = []
        value_depends_hps = []
        if isinstance(serialized_hp_value, dict):
            # when gathering the depends_hps, also allow the first entry to be a string instead of a tuple or list,
            # and assume that is the name of a single hyperparameter
            if "bounds" in serialized_hp_value.keys() and isinstance(serialized_hp_value["bounds"][1], bytes):
                this_depends_hps = serialized_hp_value["bounds"][0]
                if isinstance(this_depends_hps, str):
                    this_depends_hps = [
                        this_depends_hps,
                    ]
                value_depends_hps += list(this_depends_hps)
            if "values" in serialized_hp_value.keys() and isinstance(serialized_hp_value["values"][1], bytes):
                this_depends_hps = serialized_hp_value["values"][0]
                if isinstance(this_depends_hps, str):
                    this_depends_hps = [
                        this_depends_hps,
                    ]
                value_depends_hps += list(this_depends_hps)
            if "only" in serialized_hp_value.keys():
                this_depends_hps = serialized_hp_value["only"][0]
                if isinstance(this_depends_hps, str):
                    this_depends_hps = [
                        this_depends_hps,
                    ]
                only_depends_hps += list(this_depends_hps)

        # check if there are any dependencies
        if len(only_depends_hps) + len(value_depends_hps) == 0:
            # get the search space properties, i.e. a set of options that are needed to specify the search space entry.
            # Vacant options are populated with default values
            search_space_type, search_space_properties = _build_search_space_properties(
                hp_name, serialized_hp_value, optuna=True
            )
            non_conditional_search_space[hp_name] = (search_space_type, search_space_properties)
        else:
            conditional_search_space[hp_name] = (
                only_depends_hps,
                list(set(value_depends_hps)),
                serialized_hp_value,
            )  # remove duplicate dependencies

    # save all suggested values in case they are needed for the conditions + all fixed values to be returned later
    suggested_hps = {}
    fixed_hps = {}

    # start with non-conditional hyperparameters
    for hp_name, (hp_type, hp_properties) in non_conditional_search_space.items():
        if hp_type == "fixed":
            fixed_hps[hp_name] = hp_properties
        elif hp_type == "range":
            bounds, value_type, sampling, step, mean, std = hp_properties
            if value_type == "int":
                suggested_hps[hp_name] = trial.suggest_int(
                    hp_name, bounds[0], bounds[1], step=1 if step is None else step, log=sampling == "log"
                )
            elif value_type == "float":
                if sampling != "normal":
                    suggested_hps[hp_name] = trial.suggest_float(
                        hp_name, bounds[0], bounds[1], step=step, log=sampling == "log"
                    )
                else:
                    # Optuna does not natively support normal sampling, so calculate a normally distributed variable from
                    # a transformed, uniformly distributed variable. Since this is not added to the trial suggestions,
                    # add it to the fixed hps instead, as these are also provided to Tune.
                    fixed_hps[hp_name] = _optuna_suggest_normal(trial, hp_name, mean, std, step)
        elif hp_type == "choice":
            suggested_hps[hp_name] = trial.suggest_categorical(hp_name, hp_properties)
        else:
            raise RuntimeError(f"Unknown search space type {hp_type}.")

    # try to iteratively build conditional hyperparameters (as some conditional hyperparameters can depend on
    # other conditional hyperparameters.
    cond_hps_to_solve = list(conditional_search_space.keys())
    while len(cond_hps_to_solve) > 0:
        # to check at the end of the iteration if we could solve anything, otherwise break and raise an error
        num_left = len(cond_hps_to_solve)

        # Iterate over remaining conditional hyperparameters
        for hp_name in cond_hps_to_solve:
            only_depends_hps, value_depends_hps, serialized_hp_value = conditional_search_space[hp_name]

            # check if all depends_hps are actually in the search space
            for hp_depends in only_depends_hps + value_depends_hps:
                if hp_depends not in search_space.keys():
                    raise ValueError(
                        f"Hyperparameter '{hp_name}' depends on the value of '{hp_depends}', which is not "
                        f"part of the search space."
                    )

            # See if we can evaluate if hyperparameter is needed
            if len(only_depends_hps) > 0:
                only_depends_values = {
                    only_depends_hp: suggested_hps[only_depends_hp]
                    if only_depends_hp in suggested_hps.keys()
                    else fixed_hps[only_depends_hp]
                    if only_depends_hp in fixed_hps.keys()
                    else np.nan
                    for only_depends_hp in only_depends_hps
                }

                # None cannot be checked with np.isnan, so explicitly exclude it first
                if not any(
                    only_depends_value is not None and np.isnan(only_depends_value)
                    for only_depends_value in only_depends_values.values()
                ):
                    # evaluate the only condition
                    only_hps, serialized_only_callable = serialized_hp_value["only"]
                    need_hp = dill.loads(serialized_only_callable)(*[only_depends_values[h] for h in only_hps])
                else:
                    # we can't evaluate this only condition yet. Check the next remaining hyperparameter.
                    continue
            else:
                # no only condition, so we always need this hyperparameter
                need_hp = True

            if need_hp:
                # if this hyperparameter is needed, check if we can decide on its value
                value_depends_values = {
                    value_depends_hp: suggested_hps[value_depends_hp]
                    if value_depends_hp in suggested_hps.keys()
                    else fixed_hps[value_depends_hp]
                    if value_depends_hp in fixed_hps.keys()
                    else np.nan
                    for value_depends_hp in value_depends_hps
                }
                if not any(
                    value_depends_value is not None and np.isnan(value_depends_value)
                    for value_depends_value in value_depends_values.values()
                ):
                    # we can decide on this hyperparameter's value, so remove it from the list of remaining hyperparameters
                    cond_hps_to_solve.remove(hp_name)

                    # deserialize the hyperparameter search space entry
                    hp_value = serialized_hp_value.copy()
                    if "bounds" in serialized_hp_value.keys() and isinstance(serialized_hp_value["bounds"][1], bytes):
                        bounds_hps, serialized_bounds_callable = serialized_hp_value["bounds"]
                        hp_value["bounds"] = dill.loads(serialized_bounds_callable)(
                            *[value_depends_values[h] for h in bounds_hps]
                        )
                    if "values" in serialized_hp_value.keys() and isinstance(serialized_hp_value["values"][1], bytes):
                        values_hps, serialized_values_callable = serialized_hp_value["values"]
                        hp_value["values"] = dill.loads(serialized_values_callable)(
                            *[value_depends_values[h] for h in values_hps]
                        )

                    # calculate the search space properties of the deserialized hyperparameter search space entry
                    search_space_type, search_space_properties = _build_search_space_properties(
                        hp_name, hp_value, optuna=True
                    )

                    # finally suggest hyperparameter value
                    if search_space_type == "fixed":
                        fixed_hps[hp_name] = search_space_properties
                    elif search_space_type == "range":
                        bounds, value_type, sampling, step, mean, std = search_space_properties
                        if value_type == "int":
                            suggested_hps[hp_name] = trial.suggest_int(
                                hp_name, bounds[0], bounds[1], step=1 if step is None else step, log=sampling == "log"
                            )
                        elif value_type == "float":
                            if sampling != "normal":
                                suggested_hps[hp_name] = trial.suggest_float(
                                    hp_name, bounds[0], bounds[1], step=step, log=sampling == "log"
                                )
                            else:
                                # Optuna does not natively support normal sampling, so calculate a normally distributed variable from
                                # a transformed, uniformly distributed variable. Since this is not added to the trial suggestions,
                                # add it to the fixed hps instead, as these are also provided to Tune.
                                fixed_hps[hp_name] = _optuna_suggest_normal(trial, hp_name, mean, std, step)
                    elif search_space_type == "choice":
                        suggested_hps[hp_name] = trial.suggest_categorical(hp_name, search_space_properties)
                    else:
                        raise RuntimeError(f"Unknown search space type {hp_type}.")
                else:
                    # we can't evaluate the value condition yet, so continue to the next remaining hyperparameter
                    continue
            else:
                # we don't need this hyperparameter, so suggest a value of None, add it to the list of suggested
                # hyperparameters and drop it from the list of remaining hyperparameters. This way, stacked conditions
                # can be resolved properly as the user gets to decide what to do with hyperparameters that depend on a
                # hyperparameter that was rejected.
                cond_hps_to_solve.remove(hp_name)
                suggested_hps[hp_name] = None

        # check if we actually resolved any new hyperparameter
        if len(cond_hps_to_solve) == num_left:
            raise ValueError("Conditional search space contains circular conditions that cannot be resolved.")

    return fixed_hps


def prepare_search_space_for_PBT(
    search_space: dict[str, run_config_search_space_entry_type], best_hp_values_optuna: Optional[dict] = None
) -> tuple[tune_search_space_type, tune_search_space_type]:
    """Builds the search space for the optimization with Population Based Training.

    All hyperparameters that are not marked with 'supports_mutation' are fixed to the best values found during the
    previous optimization step. If the provided best value of a hyperparameter is ``"-"``, which by convention indicates
    an unused hyperparameter in a hierarchical search space, the corresponding hyperparameter is removed from the search
    space. If no previous optimization was performed, all hyperparameters in the search space need to be mutatable or
    fixed, otherwise an error is raised. The resulting search space is then translated to a Tune search space by calling
    ``build_tune_search_space``.

    Since the ``PopulationBasedTraining``-scheduler needs a search space that does not contain fixed values and expects
    lists instead of tune.search.sample.Categorical-instances, a second dictionary with the fixed hyperparameter values
    removed and unconverted ``'choice'`` search space entries is returned.

    Parameters
    ----------
    search_space : dict[str, run_config_search_space_entry_type]
        The search space as defined in the run-config.
    best_hp_values_optuna : Optional[dict]
        A dictionary containing the best hyperparameter values found during a previous optimization step. (Default value = None)

    Returns
    -------
    tuple[tune_search_space_type, tune_search_space_type]
        The Tune search space with non-mutatable hyperparameters fixed to their best value and the pruned Tune search
        space, containing only mutatable hyperparameters, which is to be provided to the
        ``PopulationBasedTraining``-scheduler.
    """
    # extract the hyperparameters that are marked with "supports_mutation"
    mutatable_hps = []
    non_mutatable_hps = []
    fixed_hps = []
    for hp_name, hp_value in search_space.items():
        if isinstance(hp_value, dict) and "supports_mutation" in hp_value.keys() and hp_value["supports_mutation"]:
            mutatable_hps.append(hp_name)
        elif isinstance(hp_value, dict):
            non_mutatable_hps.append(hp_name)
        else:
            fixed_hps.append(hp_name)

    # create two variants of the search space, once with only the mutatable hyperparameters and once also with
    # the fixed best values; for now, only fill the fixed hyperparameters that were fixed from the start
    search_space_mutatable = {hp_name: search_space[hp_name] for hp_name in mutatable_hps}
    search_space_with_fixed = {hp_name: search_space[hp_name] for hp_name in mutatable_hps}
    search_space_with_fixed.update({hp_name: search_space[hp_name] for hp_name in fixed_hps})

    # decide on what to do with non-mutatable, non-fixed hyperparameters
    if best_hp_values_optuna is not None:
        # if we have best values from a previous optimization step, fix these hyperparameters to their best value.
        # By convention, hyperparameters with value "-" are not needed, so disregard those.
        for hp_name in non_mutatable_hps:
            if not best_hp_values_optuna[hp_name] == "-":
                print(
                    f"Hyperparameter '{hp_name}' is not marked as mutatable. Fixing it to the best value found during "
                    f"the previous optimization step: {best_hp_values_optuna[hp_name]}."
                )
                search_space_with_fixed[hp_name] = best_hp_values_optuna[hp_name]
    else:
        # if we don't have best values to fix non-mutatable hyperparameters, all hyperparameters to optimize need to be
        # mutatable or already fixed
        assert len(non_mutatable_hps) == 0, (
            f"Hyperparameters {non_mutatable_hps} are not marked with 'support_mutation', and no prior optimization has "
            "been performed to choose fixed values from."
        )

    # convert the search spaces to Tune search spaces
    tune_search_space_with_fixed = build_tune_search_space(search_space_with_fixed)
    tune_search_space_mutatable = build_tune_search_space(search_space_mutatable, PBT=True)

    return tune_search_space_with_fixed, tune_search_space_mutatable


def add_random_seed_suggestions(seed: Optional[int] = None) -> Callable:
    """Decorator function to add a random seed to the dictionary of suggestions produced by a search algorithm.

    In order to prevent the search algorithms from trying to optimize the seed, this simple wrapper creates a subclass
    of the searcher and appends a random seed to the suggestions while leaving the rest of the searcher untouched. To
    make the added seeds deterministic, a seed needs to be provided to the wrapper that is used to generate the `numpy`
    random state.

    Parameters
    ----------
    seed : Optional[int]
        Seed to set the `numpy` random state. (Default value = None)

    Returns
    -------
    Callable
        Decorator function that uses the random state created in the outer function.
    """

    def _add_seed(cls: type) -> type:
        """Inner decorator function.

        Creates a subclass of the decorated class and overwrites the ``suggest``-function. When called, the
        ``suggest``-function of the super-class is executed and a new random number is added as key ``'seed'`` to the
        dictionary of suggestions returned by the super-class. To generate this number, the random state provided in the
        outer function is used.

        Returns
        -------
        type
            The subclass of the decorated class with the ``suggest``-function overwritten
        """

        class SearcherWithSeed(cls):
            """Subclass of the decorated class with the ``suggest``-function overwritten."""

            def suggest(self, *args: Any, **kwargs: Any) -> dict:
                """Overwrites the ``suggest``-function of the super-class to add the random seed to the suggestions.

                Parameters
                ----------
                *args : Any
                    Positional arguments of the ``suggest``-function of the super-class.
                **kwargs : Any
                    Keyword arguments of the ``suggest``-function of the super-class.

                Returns
                -------
                dict
                    The dictionary of suggestions returned by the ``suggest``-function of the super-class with the
                    random seed added as an additional entry with key ``'seed'``.
                """
                suggestion = super(SearcherWithSeed, self).suggest(*args, **kwargs)
                suggestion["seed"] = rng.randint(*OPTIMA.core.tools.get_max_seeds())
                return suggestion

        return SearcherWithSeed

    rng = np.random.RandomState(seed)
    return _add_seed
