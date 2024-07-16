# Copyright (c) 2024, InfinityQ Technology, Inc.

from unittest.mock import create_autospec, patch
import numpy as np
from titanq import Model, Vtype
from titanq.tools import configure_model_from_mps_file

def test_configure_model_from_mps_file():
    model = create_autospec(Model, instance=True)

    configure_model_from_mps_file(model, 'src/tests/test_files/mps_test.mps')

    actual_variable_calls = model.add_variable_vector.call_args_list
    expected_bounds = [(0.0, 1.0), (0.0, np.inf), (0.0, np.inf)]
    for actual_call, expected_call in zip(actual_variable_calls, expected_bounds):
        actual_var_args, _ = actual_call
        assert actual_var_args[2] == Vtype.CONTINUOUS
        np.testing.assert_array_equal(actual_var_args[3], [expected_call])
    
    actual_objective_args, _ = model.set_objective_matrices.call_args
    expected_matrix = np.zeros((3, 3), dtype=np.float32)
    expected_vector = np.array([1., 2., 1.], dtype=np.float32)
    np.testing.assert_array_equal(actual_objective_args[0], expected_matrix)
    np.testing.assert_array_equal(actual_objective_args[1], expected_vector)

    actual_eq_args, _ = model.add_equality_constraint.call_args
    expected_vector = np.array([0, -1, 1], dtype=np.float32)
    np.testing.assert_array_equal(actual_eq_args[0], expected_vector)
    assert actual_eq_args[1] == 0

    inequality_calls = model.add_inequality_constraint.call_args_list
    expected_ineq_vectors = [
        (np.array([1., 1., 0.]), [2, 4]),
        (np.array([-1., 0., -1.]), [np.nan, -3])
    ]
    for actual_call, expected_call in zip(inequality_calls, expected_ineq_vectors):
        actual_ineq_args, _ = actual_call
        np.testing.assert_array_equal(actual_ineq_args[0], expected_call[0])
        np.testing.assert_array_equal(actual_ineq_args[1], expected_call[1])
