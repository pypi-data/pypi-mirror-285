# Copyright (c) 2024, InfinityQ Technology, Inc.

class TitanqError(Exception):
    """Base TitanQ error"""

class MissingTitanqApiKey(TitanqError):
    """TitanQ Api key is missing"""

class MissingVariableError(TitanqError):
    """Variable has not already been registered"""

class VariableAlreadyExist(TitanqError):
    """Variable with the same name already exist"""

class MissingObjectiveError(TitanqError):
    """Objective has not already been registered"""

class MaximumConstraintLimitError(TitanqError):
    """The number of constraints is bigger than the number of variables"""

class ConstraintSizeError(TitanqError):
    """The constraint size does not match"""

class ConstraintAlreadySetError(TitanqError):
    """A constraint has already been set"""

class ObjectiveAlreadySetError(TitanqError):
    """An objective has already been set"""

class OptimizeError(TitanqError):
    """Error occur during optimization"""

class ServerError(TitanqError):
    """Error returned by the server"""

class ConnectionError(TitanqError):
    """Error due to a connection issue with an external resource"""

class MPSFileError(TitanqError):
    """Error due to an issue with the MPS file provided"""
