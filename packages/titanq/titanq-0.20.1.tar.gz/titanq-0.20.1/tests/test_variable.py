# Copyright (c) 2024, InfinityQ Technology, Inc.
import numpy as np
import pytest

from titanq._model.variable import BinaryVariableVector, ContinuousVariableVector, IntegerVariableVector, Vtype


@pytest.mark.parametrize("variable_vector, expected",  [
    (BinaryVariableVector('x', 3), Vtype.BINARY),
    (IntegerVariableVector('x', 3, [(1, 2)] * 3), Vtype.INTEGER),
    (ContinuousVariableVector('x', 3, [(1, 2)] * 3), Vtype.CONTINUOUS),
])
def test_variable_types(variable_vector, expected):
    assert variable_vector.vtype() == expected


@pytest.mark.parametrize("variable_vector, expected",  [
    (BinaryVariableVector('x', 3), "bbb"),
    (IntegerVariableVector('x', 4, [(1, 2)] * 4), "iiii"),
    (ContinuousVariableVector('x', 8, [(2, 6)] * 8), "cccccccc"),
])
def test_variable_types_as_list(variable_vector, expected):
    assert variable_vector.variable_types_as_list() == expected


def test_binary_variable_bounds():
    variable_vector = BinaryVariableVector("x", 3)
    assert (np.array([[0, 1], [0, 1], [0, 1]]) == variable_vector.variable_bounds()).all()

