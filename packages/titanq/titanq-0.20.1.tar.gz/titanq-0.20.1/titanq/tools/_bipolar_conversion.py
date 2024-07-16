# Copyright (c) 2024, InfinityQ Technology, Inc.

"""
Support for bipolar problems is deprecated in TitanQ.

This module can convert a bipolar problem into binary,
then the solution back from binary into bipolar.
This way, a bipolar problem can seamlessly be optimized by TitanQ
as a binary problem.
"""

import numpy as np

from typing import Optional, Tuple


class BipolarToBinary:
    """
    ℹ️ **This feature is experimental and may change.**

    Convert a bipolar problem to be solved as binary.

    TitanQ doesn't support bipolar problems directly, but these can be converted
    to binary problems instead.

    The following steps are involved:

    1. Convert the weight matrix and bias vector.
    2. Create a :class:`titanq.Model` object with binary variables,
       using the converted weight matrix and bias vector.
    3. Optimize the model.
    4. Reuse the object created in step 1 to convert the optimization
       result (result vector and objective value).

    This class assists with steps 1 and 4.

    ⚠️ Warning
    ----------

    Ensure you convert the result back to bipolar after solving the problem.
    See :meth:`convert_result`.

    Example
    -------
    >>> # Step 1: Convert the bipolar problem.
    >>> # Let weights and bias define a BIPOLAR problem.
    >>> converter = BipolarToBinary(weights=weights, bias=bias, inplace=False)
    >>>
    >>> # Step 2: Create the binary model.
    >>> model = Model()
    >>> model.add_variable_vector('x', size, Vtype.BINARY)  # Notice "Vtype.BINARY"
    >>> model.set_objective_matrices(
    >>>     converter.converted_weights(),  # Notice usage of CONVERTED weights
    >>>     converter.converted_bias(),  # Notice usage of CONVERTED bias
    >>>     Target.MINIMIZE)
    >>>
    >>> # Step 3: Optimize the binary problem.
    >>> response = model.optimize()  # Add your usual arguments here.
    >>>
    >>> # Step 4: Convert the result back to bipolar.
    >>> for objective_value, result_vector in response.result_items():
    >>>     objective_value, result_vector = converter.convert_result(
    >>>         objective_value,
    >>>         result_vector,
    >>>         inplace=False)
    """

    def __init__(
            self,
            *,
            weights: Optional[np.ndarray]=None,
            bias: np.ndarray,
            inplace: bool,
            ) -> None:
        """
        Convert a bipolar problem definition to binary and construct a
        converter for its solution (back from binary into bipolar).

        Parameters
        ----------

        weights
            Weight matrix defining the bipolar problem.
            Refer to :meth:`titanq.Model.set_objective_matrices` for
            the format.
            If ``None``, an all-zero matrix is assumed.

        bias
            Bias vector defining the bipolar problem.
            Refer to :meth:`titanq.Model.set_objective_matrices` for
            the format.

        inplace
            If ``True``, modifies the weights and bias *in-place*,
            meaning the original object is modified and no copy is
            created.
            This is useful when dealing with very large objects.

        ⚠️ Warning
        ----------

        The created object can only convert a solution
        corresponding to the inputs used to construct it.
        If used with any other problem, the conversion will be
        incorrect.
        """

        if not inplace:
            if weights is not None:
                weights = weights.copy()
            bias = bias.copy()

        self._objective_value_offset: float = _convert_problem_in_place(weights, bias)
        self._binary_weights = weights
        self._binary_bias = bias

    def converted_weights(self) -> Optional[np.ndarray]:
        """
        Return the weights converted from a bipolar problem to a binary
        one.
        Only the values change. The shape and types remain the same.

        Return ``None`` if no weights were passed in.
        See :meth:`__init__`.

        If the weights were converted in-place, then the returned
        object is the modified one, not a copy.
        """
        return self._binary_weights

    def converted_bias(self) -> np.ndarray:
        """
        Return the bias converted from a bipolar problem to a binary
        one.
        Only the values change. The shape and types remain the same.

        If the bias was converted in-place, then the returned
        object is the modified one, not a copy.
        """
        return self._binary_bias

    def convert_result(
            self,
            objective_value: float,
            result_vector: np.ndarray,
            *,
            inplace: bool,
            ) -> Tuple[float, np.ndarray]:
        """
        Take a result from a binary computation and convert it back
        to be as if it was optimized as a bipolar problem.

        ⚠️ Warning
        ----------

        The conversion uses values computed from the original
        weights and bias.
        Do not use this object to convert a solution from a
        different problem than the one used to construct it.

        Parameters
        ----------

        objective_value
            The objective value returned from the binary optimization
            response.

        result_vector
            The result vector returned from the binary optimization
            response.

        inplace
            If ``True``, modifies the result vector *in-place*,
            meaning the original object is modified and no copy is
            created.
            This is useful when dealing with very large objects.

        Returns
        -------

        The objective value and result vector that would have been
        obtained if the problem had been optimized as bipolar.

        The objective value is converted to match the original weights
        and bias, before they were converted.

        The result vector is converted to bipolar values (``{-1, 1}``)
        instead of binary values (``{0, 1}``).
        """
        if not inplace:
            result_vector = result_vector.copy()

        converted_objective_value = objective_value + self._objective_value_offset
        _convert_binary_result_to_bipolar_in_place(result_vector)
        return converted_objective_value, result_vector


def _convert_problem_in_place(
        weights: Optional[np.ndarray],
        bias: np.ndarray,
        ) -> float:
    """
    Convert a bipolar problem into a binary one, *in-place*.

    Return the objective value offset, to reconvert the solution
    back from binary to bipolar later.
    """

    objective_value_offset = _compute_objective_value_offset(weights, bias)

    _convert_bias_in_place(weights, bias)

    if weights is not None:
        _convert_weights_in_place(weights)

    return objective_value_offset


def _convert_weights_in_place(weights: np.ndarray):
    weights *= 4


def _convert_bias_in_place(
        weights: Optional[np.ndarray],
        bias: np.ndarray):

    # bias_offset = weights dot ones(num_variables)
    bias_offset: float = 0  # Assume weights are all zeros if None.
    if weights is not None:
        num_variables = weights.shape[0]
        bias_offset = weights.dot(np.ones(num_variables))

    # bias = (bias - bias_offset) * 2
    bias -= bias_offset
    bias *= 2


def _convert_binary_result_to_bipolar_in_place(result_vector: np.ndarray):
    if not np.all((result_vector == 1) | (result_vector == 0)):
        raise ValueError("The result vector is not binary. Cannot convert to bipolar.")

    # result_vector * 2 - 1
    result_vector *= 2
    result_vector -= 1


def _compute_objective_value_offset(
        weights: Optional[np.ndarray],
        bias: np.ndarray,
        ) -> float:
    """
    Compute an offset to convert an objective value from a binary
    solution to match the original bipolar problem.

    Arguments must be the _BIPOLAR_ definition of the problem,
    _BEFORE_ conversion to binary.

    Returns an offset such that:
    ``bipolar_objective_value = binary_objective_value + offset``.
    """
    num_variables = bias.shape[0]
    ones_vector = np.ones(num_variables)

    weights_contribution = 0
    if weights is not None:
        weights_contribution = 0.5 * ones_vector.dot(weights.dot(ones_vector))

    return weights_contribution - bias.dot(ones_vector)
