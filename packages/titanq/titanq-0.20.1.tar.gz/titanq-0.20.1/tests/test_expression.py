# Copyright (c) 2024, InfinityQ Technology, Inc.
import numpy as np
import pytest

from titanq._model.variable import Vtype

from .test_model import model_s3_client, mock_s3_storage, mock_metrics, mock_titanq_client, mock_result


@pytest.mark.parametrize("expr", [
    ('x'),
    (None),
    ('x+x'),
    ('x**2'),
    ('x*x'),
    ('x-x'),
    ('3*x'),
    ('4'),
    ('x*x+x'),
    ('x*x*x'),
    ('(x*x*x)[0]'),
    ('x[x]'),
    ('(np.array([1, 2, 3])*x)[0]'),
    ('(np.array([1])*x)[0]'),
    ('(np.array([1, 2])*x)'),
    ('x@x[0]'),
    ('x@(3*x[0])'),
    ('x@(x[0]+x[1])'),
    ('x@1')
])
def test_expression_single_variable_bad_cases(model_s3_client, expr):
    x = model_s3_client.add_variable_vector('x', 2)

    with pytest.raises((ValueError, IndexError, TypeError)):
        model_s3_client.set_objective_expression(eval(expr) if expr else None)


@pytest.mark.parametrize("expr,     weights, bias", [
    ('x[0]'                                     ,None              ,[1, 0]),
    ('x[1]'                                     ,None              ,[0, 1]),
    ('3*x[1]'                                   ,None              ,[0, 3]),
    ('(x*x)[0]'                                 ,[[1, 0], [0, 0]]  ,[0, 0]),
    ('(3*x*x)[0]'                               ,[[3, 0], [0, 0]]  ,[0, 0]),
    ('(x+x)[0]'                                 ,None              ,[2, 0]),
    ('3*(x+x)[0]'                               ,None              ,[6, 0]),
    ('(x-x)[0]'                                 ,None              ,[0, 0]),
    ('x[1]*x[0]'                                ,[[0, 1], [1, 0]]  ,[0, 0]),
    ('x[1]+x[0]'                                ,None              ,[1, 1]),
    ('x[1]-x[0]'                                ,None              ,[-1, 1]),
    ('(x+x+x)[0]'                               ,None              ,[3, 0]),
    ('(x*x+x)[0]'                               ,[[1, 0], [0, 0]]  ,[1, 0]),
    ('(x*(x+x))[0]'                             ,[[2, 0], [0, 0]]  ,[0, 0]),
    ('((x+x)*x)[0]'                             ,[[2, 0], [0, 0]]  ,[0, 0]),
    ('((x+x)*(x+x))[0]'                         ,[[4, 0], [0, 0]]  ,[0, 0]),
    ('((x-x)*(x+x))[0]'                         ,None              ,[0, 0]),
    ('x[0]**2'                                  ,[[1, 0], [0, 0]]  ,[0, 0]),
    ('(x[0]+x[1])**2'                           ,[[1, 2], [2, 1]]  ,[0, 0]),
    ('(3*x[0])**2'                              ,[[9, 0], [0, 0]]  ,[0, 0]),
    ('(x[0]+x[1])*2'                            ,None              ,[2, 2]),
    ('(np.array([2, 3])*x)[0]'                  ,None              ,[2, 0]),
    ('(np.array([2, 3])+x)[0]'                  ,None              ,[1, 0]),
    ('np.array([2, 3])@x'                       ,None              ,[2, 3]),
    ('x@x'                                      ,[[1, 0], [0, 1]]  ,[0, 0]),
    ('(3*x)@x'                                  ,[[3, 0], [0, 3]]  ,[0, 0]),
    ('(x+x)@x'                                  ,[[2, 0], [0, 2]]  ,[0, 0]),
    ('(x+x)@(3*x)'                              ,[[6, 0], [0, 6]]  ,[0, 0]),
    ('(x+x)@(x+x)'                              ,[[4, 0], [0, 4]]  ,[0, 0]),
    ('(x+x[1])[0]'                              ,None              ,[1, 1]),
    ('((3*x)+x[1])[0]'                          ,None              ,[3, 1]),
    ('((x+x)+x[1])[0]'                          ,None              ,[2, 1]),
    ('(np.array([2, 3])+x[0])[1]'               ,None              ,[1, 0]),
    ('(np.array([2, 3])+(x[0]*x[1]+x[0]))[1]'   ,[[0, 1], [1, 0]]  ,[1, 0]),
    ('(np.array([2, 3])*x[0])[1]'               ,None              ,[3, 0]),
    ('(np.array([2, 3])*(x[0]*x[1]+x[0]))[1]'   ,[[0, 3], [3, 0]]  ,[3, 0]),
    ('(x+x[0])[1]'                              ,None              ,[1, 1]),
    ('(x+(x[0]*x[1]+x[0]))[1]'                  ,[[0, 1], [1, 0]]  ,[1, 1]),
    ('(x*x[0])[1]'                              ,[[0, 1], [1, 0]]  ,[0, 0]),
    ('(x+x+(x[0]*x[1]+x[0]))[1]'                ,[[0, 1], [1, 0]]  ,[1, 2]),
    ('((x+x)*x[0])[1]'                          ,[[0, 2], [2, 0]]  ,[0, 0]),
    ('((x+x)+(x+x))[0]'                         ,None              ,[4, 0]),
    ('3+x[0]'                                   ,None              ,[1, 0]),
    ('3+2*x[0]'                                 ,None              ,[2, 0]),
    ('3+(2*x[0]+x[1])'                          ,None              ,[2, 1]),
    ('(2*x-1)[0]'                               ,None              ,[2, 0]),
    ('(x-2)[0]'                                 ,None              ,[1, 0]),
    ('(x@np.ones((2, 3)))[0]'                   ,None              ,[1, 1]),
    ('((x+x)@np.ones((2, 3)))[0]'               ,None              ,[2, 2]),
    ('x@np.ones((2, 2))@x'                      ,[[1, 2], [2, 1]]  ,[0, 0]),
])
def test_expression_single_variable(model_s3_client, expr, weights, bias):
    x = model_s3_client.add_variable_vector('x', 2)

    model_s3_client.set_objective_expression(eval(expr))
    # # Check the internal state
    objective_weights, objective_bias = model_s3_client.get_objective_matrices()
    np.testing.assert_equal(objective_weights, np.array(weights))
    np.testing.assert_equal(objective_bias, np.array(bias))

def test_expression_multiple_variables(model_s3_client):
    x = model_s3_client.add_variable_vector('x', 5)
    y = model_s3_client.add_variable_vector('y', 5, Vtype.CONTINUOUS, [(0.0, 0.0)]*5)
    z = model_s3_client.add_variable_vector('z', 3, Vtype.INTEGER, [(0, 0)]*3)

    expr = sum((x*3)*(y+2))-z@np.array([1, 2, 3]) + y[3]*5
    model_s3_client.set_objective_expression(expr)
    expected_weights = np.array([[0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0 ,0],
                                 [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]])
    expected_bias = np.array([6, 6, 6, 6, 6, 0, 0, 0, 5, 0, -1, -2, -3])
    # # Check the internal state
    objective_weights, objective_bias = model_s3_client.get_objective_matrices()
    np.testing.assert_equal(objective_weights,expected_weights)
    np.testing.assert_equal(objective_bias, expected_bias)