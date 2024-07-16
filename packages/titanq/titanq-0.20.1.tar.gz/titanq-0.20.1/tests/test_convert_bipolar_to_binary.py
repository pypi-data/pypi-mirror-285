# Copyright (c) 2024, InfinityQ Technology, Inc.

"""
There's a tool in the SDK to convert a bipolar problem into a binary
one that can be solved with TitanQ.

This module unit-tests that tool.

Warning: these tests are somewhat limited, as they can't guarantee the
math is right. They will only go as far as helping with refactoring.
An end-to-end test will also be useful.

Some of these tests are based on the N10 example:
https://docs.titanq.infinityq.io/quickstart/api/using-s3-buckets/putting-all-together
"""

import numpy as np
import pytest

from titanq.tools import BipolarToBinary


A_CONVERTER = BipolarToBinary(bias=np.zeros((3,), dtype=np.float32), inplace=False)


def convert_result_vector(result):
    """
    Only convert the result vector, for tests that don't care about
    objective value.
    """
    _, converted_result = A_CONVERTER.convert_result(0, result, inplace=False)
    return converted_result


def test_a_bipolar_problem_can_be_converted_to_solve_as_binary():
    INITIAL_BIPOLAR_WEIGHTS = np.array(
        [[ 0, -1, -1, -1,  1, -1,  1, -1, -1,  1],
         [-1,  0,  1, -1, -1,  1, -1, -1, -1,  1],
         [-1,  1,  0, -1,  1, -1,  1, -1, -1, -1],
         [-1, -1, -1,  0, -1,  1,  1, -1,  1, -1],
         [ 1, -1,  1, -1,  0, -1, -1,  1, -1,  1],
         [-1,  1, -1,  1, -1,  0, -1, -1,  1,  1],
         [ 1, -1,  1,  1, -1, -1,  0,  1,  1,  1],
         [-1, -1, -1, -1,  1, -1,  1,  0,  1,  1],
         [-1, -1, -1,  1, -1,  1,  1,  1,  0,  1],
         [ 1,  1, -1, -1,  1,  1,  1,  1,  1,  0]],
        dtype=np.float32)
    EXPECTED_BINARY_WEIGHTS = np.array(
        [[ 0, -4, -4, -4,  4, -4,  4, -4, -4,  4],
         [-4,  0,  4, -4, -4,  4, -4, -4, -4,  4],
         [-4,  4,  0, -4,  4, -4,  4, -4, -4, -4],
         [-4, -4, -4,  0, -4,  4,  4, -4,  4, -4],
         [ 4, -4,  4, -4,  0, -4, -4,  4, -4,  4],
         [-4,  4, -4,  4, -4,  0, -4, -4,  4,  4],
         [ 4, -4,  4,  4, -4, -4,  0,  4,  4,  4],
         [-4, -4, -4, -4,  4, -4,  4,  0,  4,  4],
         [-4, -4, -4,  4, -4,  4,  4,  4,  0,  4],
         [ 4,  4, -4, -4,  4,  4,  4,  4,  4,  0]],
        dtype=np.float32)
    INITIAL_BIPOLAR_BIAS = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        dtype=np.float32)
    EXPECTED_BINARY_BIAS = np.array(
        [6, 6, 6, 6, 2, 2,-6, 2,-2, -10],
        dtype=np.float32)

    converter = BipolarToBinary(
        weights=INITIAL_BIPOLAR_WEIGHTS,
        bias=INITIAL_BIPOLAR_BIAS,
        inplace=False)
    converted_weights = converter.converted_weights()
    converted_bias = converter.converted_bias()

    assert np.array_equal(converted_weights, EXPECTED_BINARY_WEIGHTS)
    assert np.array_equal(converted_bias, EXPECTED_BINARY_BIAS)


def test_a_bipolar_problem_is_converted_without_changing_the_original_by_default():
    initial_bipolar_weights = np.array(
        [[ 0, -1, -1, -1,  1, -1,  1, -1, -1,  1],
         [-1,  0,  1, -1, -1,  1, -1, -1, -1,  1],
         [-1,  1,  0, -1,  1, -1,  1, -1, -1, -1],
         [-1, -1, -1,  0, -1,  1,  1, -1,  1, -1],
         [ 1, -1,  1, -1,  0, -1, -1,  1, -1,  1],
         [-1,  1, -1,  1, -1,  0, -1, -1,  1,  1],
         [ 1, -1,  1,  1, -1, -1,  0,  1,  1,  1],
         [-1, -1, -1, -1,  1, -1,  1,  0,  1,  1],
         [-1, -1, -1,  1, -1,  1,  1,  1,  0,  1],
         [ 1,  1, -1, -1,  1,  1,  1,  1,  1,  0]],
        dtype=np.float32)
    initial_bipolar_bias = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        dtype=np.float32)
    UNTOUCHED_COPY_OF_INITIAL_WEIGHTS = initial_bipolar_weights.copy()
    UNTOUCHED_COPY_OF_INITIAL_BIAS = initial_bipolar_bias.copy()

    converter = BipolarToBinary(
        weights=initial_bipolar_weights,
        bias=initial_bipolar_bias,
        inplace=False)
    converted_weights = converter.converted_weights()
    converted_bias = converter.converted_bias()

    assert np.array_equal(initial_bipolar_weights, UNTOUCHED_COPY_OF_INITIAL_WEIGHTS)
    assert np.array_equal(initial_bipolar_bias, UNTOUCHED_COPY_OF_INITIAL_BIAS)
    assert converted_weights is not initial_bipolar_weights
    assert converted_bias is not initial_bipolar_bias


def test_a_bipolar_problem_can_be_converted_in_place_to_save_memory():
    weights = np.array(
        [[ 0, -1, -1, -1,  1, -1,  1, -1, -1,  1],
         [-1,  0,  1, -1, -1,  1, -1, -1, -1,  1],
         [-1,  1,  0, -1,  1, -1,  1, -1, -1, -1],
         [-1, -1, -1,  0, -1,  1,  1, -1,  1, -1],
         [ 1, -1,  1, -1,  0, -1, -1,  1, -1,  1],
         [-1,  1, -1,  1, -1,  0, -1, -1,  1,  1],
         [ 1, -1,  1,  1, -1, -1,  0,  1,  1,  1],
         [-1, -1, -1, -1,  1, -1,  1,  0,  1,  1],
         [-1, -1, -1,  1, -1,  1,  1,  1,  0,  1],
         [ 1,  1, -1, -1,  1,  1,  1,  1,  1,  0]],
        dtype=np.float32)
    EXPECTED_BINARY_WEIGHTS = np.array(
        [[ 0, -4, -4, -4,  4, -4,  4, -4, -4,  4],
         [-4,  0,  4, -4, -4,  4, -4, -4, -4,  4],
         [-4,  4,  0, -4,  4, -4,  4, -4, -4, -4],
         [-4, -4, -4,  0, -4,  4,  4, -4,  4, -4],
         [ 4, -4,  4, -4,  0, -4, -4,  4, -4,  4],
         [-4,  4, -4,  4, -4,  0, -4, -4,  4,  4],
         [ 4, -4,  4,  4, -4, -4,  0,  4,  4,  4],
         [-4, -4, -4, -4,  4, -4,  4,  0,  4,  4],
         [-4, -4, -4,  4, -4,  4,  4,  4,  0,  4],
         [ 4,  4, -4, -4,  4,  4,  4,  4,  4,  0]],
        dtype=np.float32)
    bias = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        dtype=np.float32)
    EXPECTED_BINARY_BIAS = np.array(
        [6, 6, 6, 6, 2, 2,-6, 2,-2, -10],
        dtype=np.float32)

    converter = BipolarToBinary(weights=weights, bias=bias, inplace=True)

    assert np.array_equal(weights, EXPECTED_BINARY_WEIGHTS)
    assert np.array_equal(bias, EXPECTED_BINARY_BIAS)
    assert converter.converted_weights() is weights
    assert converter.converted_bias() is bias


def test_a_bipolar_problem_without_weights_can_be_converted():
    INITIAL_BIPOLAR_BIAS = np.array(
        [1, 2, 3, -4, -5, -6, 7, 8, 9, 0],
        dtype=np.float32)
    EXPECTED_BINARY_BIAS = np.array(
        [2, 4, 6, -8, -10,-12, 14, 16, 18, 0],
        dtype=np.float32)

    converter = BipolarToBinary(bias=INITIAL_BIPOLAR_BIAS, inplace=False)
    converted_bias = converter.converted_bias()

    assert np.array_equal(converted_bias, EXPECTED_BINARY_BIAS)
    assert converter.converted_weights() is None


def test_can_convert_result_back_from_binary_to_bipolar():
    BIPOLAR_WEIGHTS = np.array(
        [[ 0, -1, -1, -1,  1, -1,  1, -1, -1,  1],
         [-1,  0,  1, -1, -1,  1, -1, -1, -1,  1],
         [-1,  1,  0, -1,  1, -1,  1, -1, -1, -1],
         [-1, -1, -1,  0, -1,  1,  1, -1,  1, -1],
         [ 1, -1,  1, -1,  0, -1, -1,  1, -1,  1],
         [-1,  1, -1,  1, -1,  0, -1, -1,  1,  1],
         [ 1, -1,  1,  1, -1, -1,  0,  1,  1,  1],
         [-1, -1, -1, -1,  1, -1,  1,  0,  1,  1],
         [-1, -1, -1,  1, -1,  1,  1,  1,  0,  1],
         [ 1,  1, -1, -1,  1,  1,  1,  1,  1,  0]],
        dtype=np.float32)
    BIPOLAR_BIAS = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        dtype=np.float32)
    EXPECTED_BIPOLAR_OBJECTIVE_VALUE = -19.0
    EXPECTED_BIPOLAR_RESULT_VECTOR = np.array(
        [-1, 1, -1, -1, 1, -1, 1, -1, 1, -1],
        dtype=np.float32)
    converter = BipolarToBinary(weights=BIPOLAR_WEIGHTS, bias=BIPOLAR_BIAS, inplace=False)

    # Let's assume we ran TitanQ, and this came out of it:
    BINARY_OBJECTIVE_VALUE = -16.0
    BINARY_RESULT_VECTOR = np.array(
        [0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
        dtype=np.float32)

    converted_objective_value, converted_result = converter.convert_result(
        BINARY_OBJECTIVE_VALUE,
        BINARY_RESULT_VECTOR,
        inplace=False)

    assert converted_objective_value == EXPECTED_BIPOLAR_OBJECTIVE_VALUE
    assert np.array_equal(converted_result, EXPECTED_BIPOLAR_RESULT_VECTOR)


def test_converting_a_result_creates_a_copy_by_default():
    binary_result_vector = np.array(
        [0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
        dtype=np.float32)
    ORIGINAL_BINARY_RESULT_VECTOR_UNTOUCHED = binary_result_vector.copy()

    converted_result = convert_result_vector(binary_result_vector)

    assert np.array_equal(binary_result_vector, ORIGINAL_BINARY_RESULT_VECTOR_UNTOUCHED)
    assert converted_result is not binary_result_vector


def test_can_convert_a_result_vector_in_place():
    BIPOLAR_WEIGHTS = np.array(
        [[ 0, -1, -1, -1,  1, -1,  1, -1, -1,  1],
         [-1,  0,  1, -1, -1,  1, -1, -1, -1,  1],
         [-1,  1,  0, -1,  1, -1,  1, -1, -1, -1],
         [-1, -1, -1,  0, -1,  1,  1, -1,  1, -1],
         [ 1, -1,  1, -1,  0, -1, -1,  1, -1,  1],
         [-1,  1, -1,  1, -1,  0, -1, -1,  1,  1],
         [ 1, -1,  1,  1, -1, -1,  0,  1,  1,  1],
         [-1, -1, -1, -1,  1, -1,  1,  0,  1,  1],
         [-1, -1, -1,  1, -1,  1,  1,  1,  0,  1],
         [ 1,  1, -1, -1,  1,  1,  1,  1,  1,  0]],
        dtype=np.float32)
    BIPOLAR_BIAS = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        dtype=np.float32)
    EXPECTED_BIPOLAR_RESULT_VECTOR = np.array(
        [-1, 1, -1, -1, 1, -1, 1, -1, 1, -1],
        dtype=np.float32)
    converter = BipolarToBinary(weights=BIPOLAR_WEIGHTS, bias=BIPOLAR_BIAS, inplace=False)

    # Let's assume we ran TitanQ, and this came out of it:
    arbitrary_objective_value = -123
    result_vector = np.array(
        [0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
        dtype=np.float32)

    _, converted_result = converter.convert_result(
        arbitrary_objective_value,
        result_vector,
        inplace=True)

    assert converted_result is result_vector
    assert np.array_equal(converted_result, EXPECTED_BIPOLAR_RESULT_VECTOR)


@pytest.mark.parametrize(
    ["invalid_binary_result"],
    [
        ([1, 2, 3, -2],),  # anything but zeros and ones
        ([0, -1, 0, 0],),  # all zeros plus an invalid value
        ([1, 1, 1, 2],),  # all ones plus an invalid value
    ])
def test_converting_a_non_binary_result_vector_raises(invalid_binary_result):
    a_non_binary_result_vector = np.array(
        invalid_binary_result,
        dtype=np.float32)

    with pytest.raises(ValueError, match="not binary"):
        convert_result_vector(a_non_binary_result_vector)


@pytest.mark.parametrize(
    ["binary", "expected_bipolar"],
    [
        ([0, 1, 0, 0, 1, 0, 1, 0, 1, 0], [-1, 1, -1, -1, 1, -1, 1, -1, 1, -1]),
        ([1, 1, 1, 1], [1, 1, 1, 1]),
        ([0, 0, 0, 0], [-1, -1, -1, -1]),
        ([], []),
    ])
def test_can_convert_result_vectors_from_binary_to_bipolar(binary, expected_bipolar):
    result_vector = np.array(
        binary,
        dtype=np.float32)

    converted_to_bipolar = convert_result_vector(result_vector)

    assert np.array_equal(converted_to_bipolar, expected_bipolar)


def test_can_convert_objective_value_without_weight_matrix():
    bipolar_bias = np.array(
        [1, 2, 3, -4, -5, -6, 7, 8, 9, 0],
        dtype=np.float32)
    EXPECTED_BIPOLAR_OBJECTIVE_VALUE = -45.0
    converter = BipolarToBinary(bias=bipolar_bias, inplace=False)
    WE_DONT_CARE_ABOUT_THE_RESULT_VECTOR = np.zeros_like(bipolar_bias)

    # Let's assume we ran TitanQ, and this came out of it:
    BINARY_OBJECTIVE_VALUE = -30.0

    converted_objective_value, _ = converter.convert_result(
        BINARY_OBJECTIVE_VALUE,
        WE_DONT_CARE_ABOUT_THE_RESULT_VECTOR,
        inplace=False)

    assert converted_objective_value == EXPECTED_BIPOLAR_OBJECTIVE_VALUE
