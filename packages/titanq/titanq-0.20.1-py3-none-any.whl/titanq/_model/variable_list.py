# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import Dict, List, Set

from .variable import VariableVector, Vtype
from .errors import VariableAlreadyExist

import numpy as np
from numpy._typing import NDArray

class VariableVectorList:
    def __init__(self) -> None:
        self._variables: List[VariableVector] = []
        self._variables_name: Set[str] = set()


    def add(self, v: VariableVector):
        """
        Add a variable vector to this list

        :param v: the new variable vector to add

        :raise VariableAlreadyExist: If a the variable to be add has the same name as an existing variable in this list
        """
        name = v.name()
        if name in self._variables_name:
            raise VariableAlreadyExist(f"variable with name: {name} has already been defined")

        self._variables_name.add(name)
        self._variables.append(v)


    def total_variable_size(self) -> int:
        """ :return: total size of all variables vector contained in the list """
        return sum(len(v) for v in self._variables)


    def n_variables(self) -> int:
        """ :return: The number of variable vector in the list """
        return len(self._variables)


    def get_variable_types_str(self) -> str:
        """
        Generate the variable types string for all the variable of this list.

        :return: The generated variable type string for all the variables
        """

        return "".join(v.variable_types_as_list() for v in self._variables)


    def has_variable_of_type(self, vtype: Vtype) -> bool:
        """:return: If any of the variable in this list has the given type"""
        return any(v.vtype() is vtype for v in self._variables)


    def variable_bounds(self) -> NDArray:
        """return the variable bounds of all variable in this list"""
        return np.concatenate([v.variable_bounds() for v in self._variables])


    def index_variables(self) -> Dict[VariableVector, int]:
        """return a dictionnary of all variable vectors with their start index in the list"""
        variables_index = {}
        current_index = 0
        for var in self._variables:
            variables_index[var] = current_index
            current_index += len(var)
        return variables_index


    def __iter__(self):
        return iter(self._variables)
