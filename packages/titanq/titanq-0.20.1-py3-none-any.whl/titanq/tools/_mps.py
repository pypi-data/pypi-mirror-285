# Copyright (c) 2024, InfinityQ Technology, Inc.

from pathlib import Path
import numpy as np

from titanq.tools._mps_loader import MPS, read_mps

from .._model.errors import MPSFileError
from .._model.model import Model
from .._model.variable import Vtype


def configure_model_from_mps_file(model: Model, file_path: Path) -> None:
    """
    Configure a model with an MPS file. Set the variable vector, the
    objective matrices and the constraints.

    Parameters
    ----------
    model
        The instance of the model to configure.
    file_path
        The path to the MPS file.
    """
    try:
        mps: MPS = read_mps(file_path)

        variables = mps.get_variables()
        var_list = list(variables.keys())
        nbr_of_variables = len(variables)
        coefficients = np.array([mps.get_objectives()[mps.objective_names()[0]]['coefficients'].get(var, 0) for var in var_list])

        for var_name, var_info in variables.items():
            var_type = var_info['type']
            var_lower = var_info['lower']
            var_upper = var_info['upper']
            if var_type == 'Integer' and var_lower == 0 and var_upper == 1:
                model.add_variable_vector(var_name, 1, Vtype.BINARY)
            elif var_type == 'Integer':
                model.add_variable_vector(var_name, 1, Vtype.INTEGER, [(var_lower, var_upper)])
            else:
                model.add_variable_vector(var_name, 1, Vtype.CONTINUOUS, [(var_lower, var_upper)])

        model.set_objective_matrices(np.zeros((nbr_of_variables, nbr_of_variables), dtype=np.float32), coefficients.astype(np.float32))

        for constr, constr_value in mps.get_constraints().items():
            constraint_mask = np.array([constr_value['coefficients'].get(var, 0) for var in var_list])
            rhs = mps.get_rhs()[constr]
            if constr_value['type'] == 'G':
                constraint_bounds = np.array([rhs, np.nan])
                if mps.get_ranges().get(constr) is not None:
                    constraint_bounds[1] = rhs+mps.get_ranges().get(constr)['upper']
                model.add_inequality_constraint(constraint_mask.astype(np.float32), constraint_bounds.astype(np.float32))

            elif constr_value['type'] == 'L':
                constraint_bounds = np.array([np.nan, rhs])
                if mps.get_ranges().get(constr) is not None:
                    constraint_bounds[0] = rhs+mps.get_ranges().get(constr)['lower']
                model.add_inequality_constraint(constraint_mask.astype(np.float32), constraint_bounds.astype(np.float32))

            elif constr_value['type'] == 'E':
                model.add_equality_constraint(constraint_mask.astype(np.float32), mps.get_rhs().get(constr, 0))

    except Exception as e:
        raise MPSFileError(str(e))