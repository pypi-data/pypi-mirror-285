# Copyright (c) 2024, InfinityQ Technology, Inc.

import io
import json
import logging
import numpy as np
import os
import zipfile
from typing import Any, Dict, List, Optional, Tuple, Union
from warnings import warn

from .constraints import Constraints
from .errors import (
    ConstraintAlreadySetError,
    MissingObjectiveError,
    MissingVariableError,
    MissingTitanqApiKey,
    ObjectiveAlreadySetError,
    OptimizeError,
)
from .expression_parser import objective_matrices_from_expression
from .objective import Objective, Target
from .optimize_response import OptimizeResponse
from .manifest import Manifest
from .variable import (
    BinaryVariableVector,
    ContinuousVariableVector,
    Expression,
    IntegerVariableVector,
    VariableVector,
    Vtype,
)
from .._client import api_model, Client
from .._storage import ManagedStorage, StorageClient
from .numpy_util import (
    is_ndarray_binary,
    is_upperbound_bigger_equal_lowerbound,
    ndarray_contains_nan_inf,
    reshape_to_2d,
    validate_cardinalities
)
from .variable_list import VariableVectorList

log = logging.getLogger("TitanQ")


class Model:
    """
    Root object to define a problem to be optimized
    """

    def __init__(
        self,
        *,
        api_key: str = None,
        storage_client: StorageClient = None,
        base_server_url: str = "https://titanq.infinityq.io"
        ) -> None:
        """
        Initiate the model with a storage client. If the storage_client is missing, the storage will be managed by TitanQ.

        Notes
        -----
        The storage managed by TitanQ supports weight matrices with a size up to 10k only.

        Parameters
        ----------
        api_key
            TitanQ API key to access the service.
            If not set, it will use the environment variable ``TITANQ_API_KEY``
        storage_client
            Storage to choose in order to store some items.
        base_server_url
            TitanQ API server url, default set to ``https://titanq.infinityq.io``.

        Raises
        ------
        MissingTitanqApiKey
            If no API key is set and is also not set as an environment variable

        Examples
        --------
        With an S3 storage client
            >>> from titanq import Model, S3Storage
            >>> storage_client = S3Storage(
                access_key="{insert aws bucket access key here}",
                secret_key="{insert aws bucket secret key here}",
                bucket_name="{insert bucket name here}"
            )
            >>> model = Model(storage_client)

        Managed storage client
            >>> from titanq import Model, S3Storage
            >>> model = Model()
        """
        self._variables = VariableVectorList()
        self._objective: Objective = None
        self._constraints = Constraints()

        api_key = api_key or os.getenv("TITANQ_API_KEY")
        if api_key is None:
            raise MissingTitanqApiKey(
                "No API key is provided. You can set your API key in the Model, "
                + "or you can set the environment variable TITANQ_API_KEY")

        self._titanq_client = Client(api_key, base_server_url)
        self._manifest: Manifest = Manifest()

        # the user chose a managed storage or left it as default
        if storage_client is None:
            storage_client = ManagedStorage(self._titanq_client)

        self._storage_client = storage_client


    def get_objective_matrices(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Retrieve the weights and bias vector from the model's objective. Both will be None
        if not set.

        Return
        ------
        Weights matrix if not None and bias vector if not None
        """
        weights = self._objective.weights() if self._objective else None
        bias = self._objective.bias() if self._objective else None
        return (weights, bias)


    def add_variable_vector(
        self,
        name: str = '',
        size: int = 1,
        vtype: Vtype = Vtype.BINARY,
        variable_bounds:
            Optional[
                Union[
                    List[Tuple[int, int]],
                    List[Tuple[float, float]],
                ]
            ]=None,
    ) -> VariableVector:
        """
        Add a vector of variable to the model. Multiple variables vector can be added but with different names.

        Notes
        -----
        If Vtype is set to ``Vtype.INTEGER`` or ``Vtype.CONTINUOUS``, variable_bounds need to be set.

        Parameters
        ----------
        name
            The name given to this variable vector.
        size
            The size of the vector.
        vtype
            Type of the variables inside the vector.
        variable_bounds
            Lower and upper bounds for the variable vector. A list of tuples (can be either integers or continuous)

        Return
        ------
        variable
            The variable vector created.

        Raises
        ------
        MaximumVariableLimitError
            If the total size of variables exceed the limit.
        ValueError
            If the size of the vector is < 1

        Examples
        --------
        >>> from titanq import Model, Vtype
        >>> model.add_variable_vector('x', 3, Vtype.BINARY)
        >>> model.add_variable_vector('y', 2, Vtype.INTEGER, [[0, 5], [1, 6]])
        >>> model.add_variable_vector('z', 3, Vtype.CONTINUOUS, [[2.3, 4.6], [3.1, 5.3], [1.1, 4]])
        """

        if not variable_bounds:
            variable_bounds = []

        # validation
        if not self._constraints.is_empty():
            raise ConstraintAlreadySetError("Cannot add additional variable once constraints have been defined")

        if self._objective is not None:
            raise ObjectiveAlreadySetError("Cannot add additional variable once objective have been defined")

        # create the Variable vector
        if vtype is Vtype.BINARY:
            if variable_bounds:
                raise ValueError("variable_bounds is not supported with Vtype.BINARY")
            variables = BinaryVariableVector(name, size)

        elif vtype is Vtype.INTEGER:
            variables = IntegerVariableVector(name, size, variable_bounds)

        elif vtype is Vtype.CONTINUOUS:
            variables = ContinuousVariableVector(name, size, variable_bounds)

        else:
            raise NotImplementedError(f"Unsupported variable type: {vtype}")

        self._variables.add(variables)
        self._constraints.augment_size(size)

        log.debug(f"add variable name='{name}', type={str(vtype)}, size={size}.")

        return variables

    def set_objective_expression(self, expr: Expression, target=Target.MINIMIZE):
        """
        ℹ️ **This feature is experimental and may change.**

        Sets the objective function for the optimization problem using the given expression.

        This method processes the provided expression to extract the bias vector and weight matrix,
        and then sets these as the objective matrices for the optimization problem.

        Parameters
        ----------
        expr
            The expression defining the objective function. This should be an instance of `Expression`.
        target
            The target of this objective matrix.

        Raises
        ------
        ValueError
            if the provided expression contains any invalid/unsupported input

        Examples
        --------
        >>> from titanq import Model, Vtype
        >>> x = model.add_variable_vector('x', 2, Vtype.BINARY)
        >>> y = model.add_variable_vector('y', 2, Vtype.BINARY)
        >>> expr = (np.array([3, 4]) * x + (x * y) - 5 * y)[0]
        >>> model.set_objective_expression(expr)
        """
        weights, bias = objective_matrices_from_expression(expr, self._variables)
        self.set_objective_matrices(weights, bias, target)

    def set_objective_matrices(self, weights: Optional[np.ndarray], bias: np.ndarray, target=Target.MINIMIZE):
        """
        Set the objective matrices for the model.

        Parameters
        ----------
        weights
            The quadratic objective matrix, **this matrix needs to be symmetrical**.
            A NumPy 2-D dense ndarray (must be float32).
            Weights matrix can be set to **None** if it is a linear problem with no quadratic elements.
        bias
            The linear constraint vector. A NumPy 1-D ndarray.
        target
            The target of this objective matrix.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ObjectiveAlreadySetError
            If an objective has already been set in this model.
        ValueError
            If the weights shape or the bias shape does not fit the variables in the model.
            If the weights or bias data type is not float32.

        Examples
        --------
        >>> from titanq import Model, Target
        >>> edges = {0:[4,5,6,7], 1:[4,5,6,7], 2:[4,5,6,7], 3:[4,5,6,7], 4:[0,1,2,3], 5:[0,1,2,3], 6:[0,1,2,3], 7:[0,1,2,3]}
        >>> size = len(edges)
        >>> weights = np.zeros((size, size), dtype=np.float32)
        >>> for root, connections in edges.items():
        >>>     for c in connections:
        >>>         weights[root][c] = 1
        >>> # construct the bias vector (Uniform weighting across all nodes)
        >>> bias = np.asarray([0]*size, dtype=np.float32)
        >>> model.set_objective_matrices(weights, bias, Target.MINIMIZE)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set objective before adding a variable to the model.")

        if self._objective is not None:
            raise ObjectiveAlreadySetError("An objective has already have been set for this model.")

        log.debug(f"set objective matrix and bias vector.")

        self._objective = Objective(self._variables.total_variable_size(), weights, bias, target)


    def add_set_partitioning_constraints_matrix(self, constraint_mask: np.ndarray):
        """
        Adds set partitioning constraints in matrix format to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (must be binary).
            The constraint_mask matrix of shape (M, N) where M the number of constraints and N is the number of variables.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraints exceed the limit.
        ConstraintSizeError
            If the constraint_mask shape does not fit the expected shape of this model.
        ValueError
            If the constraint_mask data type is not binary.

        Examples
        --------
        >>> constraint_mask = np.array([[1, 1, 1, 0, 1], [1, 1, 1, 1, 0]])
        >>> model.add_set_partitioning_constraints_matrix(constraint_mask)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_set_partitioning_constraints_matrix() function with a vector, " \
                "please use add_set_partitioning_constraint() instead")

        if not is_ndarray_binary(constraint_mask):
            raise ValueError(f"Cannot add a constraint if the values are not in binary.")

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=np.ones((constraint_mask.shape[0],2))
        )
        self._manifest.activate_set_partitioning_constraint()

    def add_set_partitioning_constraint(self, constraint_mask: np.ndarray):
        """
        Adds set partitioning constraint vector to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (must be binary).
            The constraint_mask vector of shape (N,) where N is the number of variables.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraint exceed the limit.
        ConstraintSizeError
            If the constraint_mask shape does not fit the expected shape of this model.
        ValueError
            If the constraint_mask data type is not binary.

        Examples
        --------
        >>> constraint_mask = np.array([1, 1, 1, 0, 1])
        >>> model.add_set_partitioning_constraint(constraint_mask)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use this add_set_partitioning_constraint() function with a matrix, " \
                "please use add_set_partitioning_constraints_matrix() instead")

        self.add_set_partitioning_constraints_matrix(reshape_to_2d(constraint_mask))


    def add_cardinality_constraints_matrix(self, constraint_mask: np.ndarray, cardinalities: np.ndarray):
        """
        Adds cardinality constraints in matrix format to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (must be binary).
            The constraint_mask matrix of shape (M, N) where M the number of constraints and N is the number of variables.
        cardinalities
            A NumPy 1-D ndarray (must be non-zero unsigned integer).
            The constraint_rhs vector of shape (M,) where M is the number of constraints.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraint exceed the limit.
        ConstraintSizeError
            If the constraint_mask shape or the constraint_rhs shape does not fit the expected shape of this model.
        ValueError
            If the constraint_mask is not binary or cardinalities data type are not unsigned integers.

        Examples
        --------
        >>> constraint_mask = np.array([[1, 1, 1, 0, 1], [1, 1, 1, 1, 0]])
        >>> cardinalities = np.array([3, 2])
        >>> model.add_cardinality_constraints_matrix(constraint_mask, cardinalities)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_cardinality_constraints_matrix() function with a vector, " \
                "please use add_cardinality_constraint() instead")

        if cardinalities.ndim != 1:
            raise ValueError(f"Cannot set constraints if cardinalities is not a NumPy 1-D dense ndarray")

        if not np.issubdtype(cardinalities.dtype, np.integer):
            raise ValueError("Found cardinalities data types not integer")

        if not np.all(cardinalities > 0):
            raise ValueError("Found cardinalities data types not unsigned integer")

        if not is_ndarray_binary(constraint_mask):
            raise ValueError(f"Cannot add a constraint if the values are not in binary.")

        if cardinalities.shape[0] != constraint_mask.shape[0]:
            raise ValueError(
                f"Cannot set constraints if cardinalities shape is not the same as the expected shape of this model." \
                f" Got cardinalities shape: {cardinalities.shape[1]}, constraint mask shape: {constraint_mask.size()}.")

        validate_cardinalities(constraint_mask, cardinalities)

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=np.repeat(cardinalities, 2).reshape(-1, 2)
        )
        self._manifest.activate_cardinality_constraint()


    def add_cardinality_constraint(self, constraint_mask: np.ndarray, cardinality: int):
        """
        Adds cardinality constraint vector to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (must be binary).
            The constraint_mask vector of shape (N,) where N is the number of variables.
        cardinality
            The constraint_rhs cardinality.
            This value has to be a non-zero unsigned integer.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            If the number of constraints exceed the limit.
        ConstraintSizeError
            If the constraint_mask shape or the constraint_rhs shape does not fit
            the expected shape of this model.
        ValueError
            If the constraint_mask is not in binary or the cardinality is not an unsigned integer.

        Examples
        --------
        >>> constraint_mask = np.array([1, 1, 1, 0, 1])
        >>> cardinality = 3
        >>> model.add_cardinality_constraint(constraint_mask, cardinality)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_cardinality_constraint() function with a matrix, " \
                "please use add_cardinality_constraints_matrix() instead")

        self.add_cardinality_constraints_matrix(reshape_to_2d(constraint_mask), np.full((1,), cardinality))


    def add_equality_constraints_matrix(self, constraint_mask: np.ndarray, limit: np.ndarray) -> None:
        """
        Adds an equality constraint matrix to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (float32).
            The constraint_mask vector of shape (M, N) where M the number of constraints and N is the number of variables.
        limit
            A NumPy 1-D array (float32).
            The limit vector of shape (M,) where M is the number of constraints.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraint exceed the limit.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask or limit contains irregular format ('NaN' or 'inf').

        Examples
        --------
        >>> constraint_mask = np.array([[-3.51, 0, 0, 0], [10, 0, 0, 0]], dtype=np.float32)
        >>> limit = np.array([2, 10], dtype=np.float32)
        >>> model.add_equality_constraints_matrix(constraint_mask, limit)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.dtype != np.float32 or limit.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got Constraint mask: {constraint_mask.dtype}, Limit: {limit.dtype}")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_equality_constraint_matrix() function with a vector, " \
                "please use add_equality_constraint() instead")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Constraint mask contains NaN  or inf values")

        if limit.ndim != 1:
            raise ValueError("Limit must be a NumPy 1-D array")

        if ndarray_contains_nan_inf(limit):
            raise ValueError("Limit contains NaN or inf values")

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=np.repeat(limit, 2).reshape(-1, 2)
        )
        self._manifest.activate_equality_constraint()

    def add_equality_constraint(self, constraint_mask: np.ndarray, limit: np.float32) -> None:
        """
        Adds an equality constraint vector to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (float32).
            The constraint_mask vector of shape (N,) where N is the number of variables.
        limit
            Limit value to the constraint mask.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraint exceed the limit.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask or limit contains irregular format ('NaN' or 'inf').

        Examples
        --------
        >>> constraint_mask = np.array([1.05, -1.1], dtype=np.float32)
        >>> limit = -3.45
        >>> model.add_equality_constraint(constraint_mask, limit)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_equality_constraint() function with a matrix, " \
                "please use add_equality_constraint_matrix() instead")

        self.add_equality_constraints_matrix(reshape_to_2d(constraint_mask), np.full((1,), limit, dtype=np.float32))


    def add_inequality_constraints_matrix(self, constraint_mask: np.ndarray, constraint_bounds: np.ndarray):
        """
        Adds inequality constraint matrix to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (float32).
            The constraint_mask vector of shape (M, N) where N is the number of variables.
        constraint_bounds
            A NumPy 2-D ndarray (float32).
            Vector of shape (M, 2) where M is the number of constraints.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraint exceed the limit.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask contains irregular format ('NaN' or 'inf').
            If the lowerbound is equal or higher than its given upperbound.

        Examples
        --------
        >>> constraint_mask = np.array([[-3.51, 0], [10, 0]], dtype=np.float32)
        >>> constraint_bounds = np.array([[8, 9], [np.nan, 100_000]], dtype=np.float32)
        >>> model.add_inequality_constraints_matrix(constraint_mask, constraint_bounds)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.dtype != np.float32 or constraint_bounds.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got Constraint mask: {constraint_mask.dtype}, Limit: {constraint_bounds.dtype}")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_inequality_constraint_matrix() function with a vector, " \
                "please use add_inequality_constraint() instead")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Constraint mask contains NaN  or inf values.")

        if is_upperbound_bigger_equal_lowerbound(constraint_bounds):
            raise ValueError("Constraint bounds contains lowerbounds equal or higher than their upperbound.")

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=constraint_bounds
        )
        self._manifest.activate_inequality_constraint()


    def add_inequality_constraint(self, constraint_mask: np.ndarray, constraint_bounds: np.ndarray):
        """
        Adds inequality constraint vector to the model. At least one bound must be set.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (float32).
            The constraint_mask vector of shape (N,) where N is the number of variables.
        constraint_bounds
            A NumPy 1-D ndarray (float32).
            Vector of shape (2,)

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MaximumConstraintLimitError
            The number of constraint exceed the limit.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask contains irregular format ('NaN' or 'inf').
            If the lowerbound is equal or higher than the upperbound.

        Examples
        --------
        >>> constraint_mask = np.array([1.05, -1.1], dtype=np.float32)
        >>> constraint_bounds = np.array([1.0, np.nan], dtype=np.float32)
        >>> model.add_inequality_constraint(constraint_mask, constraint_bounds)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_inequality_constraint() function with a matrix, " \
                "please use add_inequality_constraint_matrix() instead")

        self.add_inequality_constraints_matrix(reshape_to_2d(constraint_mask), reshape_to_2d(constraint_bounds))


    def optimize(
        self,
        *,
        beta: List[float] = [0.1],
        coupling_mult: float = 0.5,
        timeout_in_secs: float = 10.0,
        num_chains: int = 8,
        num_engines: int = 1,
        penalty_scaling: float = None
    ) -> OptimizeResponse:
        """
        Optimize this model.

        Notes
        -----
        All of the files used during this computation will be cleaned at the end.
        For more information on how to tunes those parameters, visit the API doc at `TitanQ API <https://docs.titanq.infinityq.io/>`_ and the `tuning guide <https://docs.titanq.infinityq.io/quickstart/parameter_tuning_guide>`_.

        Parameters
        ----------
        beta
            ``beta`` hyper parameter used by the solver.
        coupling_mult
            ``coupling_mult`` hyper parameter used by the solver.
        timeout_in_secs
            Maximum time (in seconds) the solver can take to solve this problem.
        num_chains
            ``num_chains`` hyper parameter used by the solver.
        num_engines
            ``num_engines`` hyper parameter used by the solver.
        penalty_scaling
            ``penalty_scaling`` hyper parameter used by the solver.

        Returns
        -------
        OptimizeResponse
            Optimized response data object

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MissingObjectiveError
            If no objective matrices have been added to the model.

        Examples
        --------
        basic solve
            >>> response = model.optimize(timeout_in_secs=60)
        multiple engine
            >>> response = model.optimize(timeout_in_secs=60, num_engines=2)
        custom values
            >>> response = model.optimize(beta=[0.1], coupling_mult=0.75, num_chains=8)
        print values
            >>> print("-" * 15, "+", "-" * 26, sep="")
            >>> print("Ising energy   | Result vector")
            >>> print("-" * 15, "+", "-" * 26, sep="")
            >>> for ising_energy, result_vector in response.result_items():
            >>>     print(f"{ising_energy: <14f} | {result_vector}")
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot optimize before adding a variable to the model.")

        if self._objective is None:
            raise MissingObjectiveError("Cannot optimize before adding an objective to the model.")

        result, metrics = self._solve(beta, coupling_mult, timeout_in_secs, num_chains, num_engines, penalty_scaling)

        return OptimizeResponse(self._variables, result, metrics)

    def _solve(
        self,
        beta: List[float],
        coupling_mult: float,
        timeout_in_secs: float,
        num_chains: int,
        num_engines: int,
        penalty_scaling: Optional[float],
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        issue a solve request and wait for it to complete.

        Parameters
        ----------
        beta
            beta hyper parameter used by the backend solver.
        coupling_mult
            coupling_mult hyper parameter used by the backend solver.
        timeout_in_secs
            Maximum time (in seconds) the backend solver can take to resolve this problem.
        num_chains
            num_chains hyper parameter used by the backend solver.
        num_engines
            num_engines parameter used by the backend solver.

        Returns
        -------
        The result numpy array and the metric json object.
        """
        with self._storage_client.temp_files_manager(
            self._objective.bias(),
            self._objective.weights(),
            self._constraints.bounds() if self._constraints else None,
            self._constraints.weights() if self._constraints else None,
            # variables bounds is only sent if variable is set to binary
            self._variables.variable_bounds(),
        ) as temp_files:

            # api request
            request = api_model.SolveRequest(
                input=temp_files.input(),
                output=temp_files.output(),
                parameters=api_model.Parameters(
                    beta=beta,
                    coupling_mult=coupling_mult,
                    num_chains=num_chains,
                    num_engines=num_engines,
                    penalty_scaling=penalty_scaling,
                    timeout_in_secs=timeout_in_secs,
                    variable_types=self._variables.get_variable_types_str()
                )
            )

            # adding manifest flags to the request
            request.input.manifest = api_model.Manifest(
                has_set_partitioning_constraint=self._manifest.has_set_partitioning_constraint(),
                has_cardinality_constraint=self._manifest.has_cardinality_constraint(),
                has_equality_constraint=self._manifest.has_equality_constraint(),
                has_inequality_constraint=self._manifest.has_inequality_constraint()
            )

            solve_response = self._titanq_client.solve(request)

            # wait for result to be uploaded by the solver and download it
            archive_file_content = temp_files.download_result()
            with zipfile.ZipFile(io.BytesIO(archive_file_content), 'r') as zip_file:
                try:
                    metrics_content = zip_file.read("metrics.json")
                    result_content = zip_file.read("result.npy")
                except KeyError as ex:
                    try:
                        error_content = zip_file.read("error.json")
                        raise OptimizeError(json.loads(error_content)["error"]) from ex
                    except KeyError as e:
                        raise OptimizeError(
                            "Unexpected error in the solver, please contact InfinityQ support for more help" \
                            f" and provide the following computation id {solve_response.computation_id}") from e

        log.debug("Optimization completed")
        return np.load(io.BytesIO(result_content)), json.loads(metrics_content)
