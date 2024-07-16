# Copyright (c) 2024, InfinityQ Technology, Inc.
"""
``OptimizeResponse`` data object that is returned from the model when optimizing a problem.
"""

import logging
from typing import Any, Dict, List, Tuple, Union
import uuid
import warnings

import numpy as np

from .variable_list import VariableVectorList

log = logging.getLogger('TitanQ')

class OptimizeResponse:
    """
    Object containing the optimization results and all of the metrics returned by the solver.
    """
    def __init__(self, variable_list: VariableVectorList, result_array: np.ndarray, metrics: Dict[str, Any]) -> None:
        self._result_by_variable: Dict[str, np.ndarray] = {}
        start_index = 0

        # extract all the result for each given variable
        # The result array is a 2d array where each line is a different result of the same problem
        for variable_vector in  variable_list:

            result_for_this_variable = []
            last_index = start_index + len(variable_vector)

            for full_result in result_array:
                result_extracted = full_result[start_index: last_index]
                result_for_this_variable.append(result_extracted)

            self._result_by_variable[variable_vector.name()] = np.array(result_for_this_variable)
            start_index = last_index

        self._metrics = metrics
        self._all_results = result_array


    def __getattr__(self, attr: str):
        # if attribute is the name of a variable
        try:
            return self._result_by_variable[attr]
        except KeyError:
            pass

        # This is to keep compatibility with older version of SDK
        if attr == "ising_energy":
            try:
                return self.__getattr__("solutions_objective_value")
            except (AttributeError, KeyError):
                pass


        warnings.warn(
            'Obtaining metrics directly as an attribute is deprecated. Use computation_metrics() or original_input_params() instead.',
            DeprecationWarning,
            stacklevel=2
        )


        # check inside computation metrics and original params for the attribute
        try:
            return self.computation_metrics(attr)
        except KeyError:
            pass

        try:
            return self.original_input_params(attr)
        except KeyError:
            pass

        # was not found, try the older behavior
        try:
            return self._metrics[attr]
        except KeyError:
            raise AttributeError(attr)


    def result_vector(self) -> np.ndarray:
        """
        The result vector

        Returns
        -------
        The result vector of this optimization.
        """
        return self._all_results


    def result_items(self) -> List[Tuple[float, np.ndarray]]:
        """
        ex. [(-10000, [0, 1, 1, 0]), (-20000, [1, 0, 1, 0]), ...]

        Returns
        -------
        List of tuples containing the solutions objective value and its corresponding result vector
        """

        solutions_objective_value = self.ising_energy
        return [(solutions_objective_value[i], self._all_results[i]) for i in range(len(self._all_results))]


    def computation_metrics(self, key: str = None) -> Any:
        """
        The computation metrics the solver returnes

        Returns
        -------
        All computation metrics if no key is given of the specific metrics with the associated key if one is provided.

        Raises
        ------
        KeyError
            The given key does not exist.
        """
        metrics = self._metrics['computation_metrics']
        if key:
            metrics = metrics[key]
        return metrics


    def computation_id(self) -> uuid.UUID:
        """
        The computation id is a Universal unique id that identify this computation inside the TitanQ platform.

        Provide this id on any support request to the InfinityQ.

        Returns
        -------
        The computation id of this solve.
        """
        return self._metrics['computation_id']


    def original_input_params(self, key: str = None) -> Any:
        """
        The original input params sent to the solver

        Returns
        -------
        All original params if no key is given. A specific param with the associated key if one is provided.

        Raises
        ------
        KeyError
            The given key does not exist
        """
        metrics = self._metrics['original_input_params']
        if key:
            metrics = metrics[key]
        return metrics


    def metrics(self, key: str = None) -> Union[str, Dict[str, Any]]:
        """
        .. deprecated:: 0.7.0
            Use computation_metrics() or original_input_params() instead.

        Returns
        -------
        All metrics if no key is given. A specific metric with the associated key if one is provided.

        Raises
        ------
        KeyError
            The given key does not exist
        """
        warnings.warn(
            'Calling metrics() is deprecated. Use computation_metrics() or original_input_params() instead.',
            DeprecationWarning,
            stacklevel=2
        )
        if key:
            return self._metrics[key]
        else:
            return self._metrics
