# Copyright (c) 2024, InfinityQ Technology, Inc.

import abc
import enum
from typing import List, Optional, Tuple, Union
import numpy as np
from numpy._typing import NDArray

class Vtype(str, enum.Enum):
    """
    All variable types currently supported by the solver.

    ℹ️ **NOTE:** Bipolar variables are not directly supported,
    but :class:`tools.BipolarToBinary` can be used as an alternative.
    """

    BINARY = 'binary'
    INTEGER = 'integer'
    CONTINUOUS = 'continuous'

    def __str__(self) -> str:
        return str(self.value)


class ArithmeticMixin(abc.ABC):
    """abstract class that overrides the operators"""

    def __mul__(self, other):
        return mul_dispatcher(self, other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __matmul__(self, other):
        return matmul_dispatcher(self, other)

    def __rmatmul__(self, other):
        return self.__matmul__(other)

    def __add__(self, other):
        return add_dispatcher(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + other * -1

    def __pow__(self, other):
        if other == 2:
            return self * self
        raise ValueError(f"Only powers of 2 are supported.")


class VariableVector(ArithmeticMixin, abc.ABC):
    """
    Object That represent a vector of variable to be optimized.
    """

    # Disable NumPy's (ufuncs) to avoid unintended operations on this class with array
    __array_ufunc__ = None
    def __init__(self, name: str, size: int) -> None:
        if size < 1:
            raise ValueError("Variable vector size cannot be less than 1")

        self._name = name
        self._size = size
        self._iter = 0


    def __len__(self) -> int:
        return self._size


    def __getitem__(self, other) -> 'SubVariable':
        return SubVariable(self, other)
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._iter >= self._size:
            raise StopIteration

        self._iter += 1
        return self[self._iter]


    def name(self) -> str:
        """
        :return: Name of this variable vector.
        """
        return self._name

    @abc.abstractmethod
    def vtype(self) -> Vtype:
        """
        :return: Type of variable in the vector.
        """


    @abc.abstractmethod
    def variable_types_as_list(self) -> str:
        """
        :return: Generate a string of 'b', 'i' or 'c' depending on the variable type
        """


    @abc.abstractmethod
    def variable_bounds(self) -> NDArray:
        """
        :return: The variable bounds associated to this variable vector
        """


class BinaryVariableVector(VariableVector):
    def vtype(self) -> Vtype:
        return Vtype.BINARY


    def variable_types_as_list(self) -> str:
        return "b" * len(self)


    def variable_bounds(self) -> NDArray:
        return np.tile(np.array([0,1], dtype=np.float32), (self._size, 1))


class IntegerVariableVector(VariableVector):
    def __init__(self, name: str, size: int, variable_bounds: List[Tuple[int, int]]) -> None:
        super().__init__(name, size)

        if len(variable_bounds) != len(self):
            raise ValueError("variable_bounds need to be the same length as variable size")

        self._variable_bounds = np.array(variable_bounds, dtype=np.float32)


    def vtype(self) -> Vtype:
        return Vtype.INTEGER


    def variable_types_as_list(self) -> str:
        return "i" * len(self)


    def variable_bounds(self) -> NDArray:
        return self._variable_bounds

class ContinuousVariableVector(VariableVector):
    def __init__(self, name: str, size: int, variable_bounds: List[Tuple[int, int]]) -> None:
        super().__init__(name, size)

        if len(variable_bounds) != len(self):
            raise ValueError("variable_bounds need to be the same length as variable size")

        self._variable_bounds = np.array(variable_bounds, dtype=np.float32)


    def vtype(self) -> Vtype:
        return Vtype.CONTINUOUS


    def variable_types_as_list(self) -> str:
        return "c" * len(self)


    def variable_bounds(self) -> NDArray:
        return self._variable_bounds


##############################
# Expression related classes #
##############################
class SubVariable(ArithmeticMixin):
    """sub variable of a variable vector"""
    __array_ufunc__ = None
    def __init__(
        self,
        parent: VariableVector,
        index: int
    ) -> None:
        self._parent = parent
        self._index = index

    def parent(self) -> VariableVector:
        return self._parent

    def index(self) -> int:
        return self._index


class Term(ArithmeticMixin):
    __array_ufunc__ = None
    def __init__(
        self,
        v1: SubVariable,
        v2: Optional[SubVariable],
        coeff: float
    ) -> None:
        self._v1 = v1
        self._v2 = v2
        self._coeff = coeff

    def v1(self) -> SubVariable:
        return self._v1

    def v2(self) -> Optional[SubVariable]:
        return self._v2

    def coeff(self) -> float:
        return self._coeff


class Expression(ArithmeticMixin):
    __array_ufunc__ = None
    def __init__(
        self,
        terms: List[Union[Term, float, int]] = []
    ) -> None:
        self._terms = terms

    def terms(self) -> List[Union[Term, float, int]]:
        return self._terms


class VectorExpression(ArithmeticMixin):
    __array_ufunc__= None
    def __init__(self, expressions: List[Expression]):
        self._expressions = expressions

    def __len__(self) -> int:
        return len(self._expressions)

    def __getitem__(self, other) -> Expression:
        return self.expressions()[other]

    def expressions(self) -> List[Expression]:
        return self._expressions


def add_dispatcher(
    lhs: Union[Expression, SubVariable, Term, VariableVector, VectorExpression],
    rhs: Union[np.ndarray, Expression, SubVariable, Term, VariableVector, VectorExpression]
) -> Union[Expression, Term, VectorExpression]:
    """addition dispatch to the right operation"""
    if isinstance(lhs, SubVariable):
        if isinstance(rhs, SubVariable):
            return Expression([Term(lhs, None, 1), Term(rhs, None, 1)])
        if is_numeric(rhs) or isinstance(rhs, Term):
            return Expression([Term(lhs, None, 1), rhs])
        if isinstance(rhs, Expression):
            return Expression([Term(lhs, None, 1)] + rhs.terms())

    if isinstance(lhs, Term):
        if is_numeric(rhs) or isinstance(rhs, Term):
            return Expression([lhs, rhs])

    if isinstance(lhs, Expression):
        if isinstance(rhs, Expression):
            return Expression(lhs.terms() + rhs.terms())
        if is_numeric(rhs) or isinstance(rhs, Term):
            return Expression([rhs] + lhs.terms())

    if isinstance(lhs, (SubVariable, Term, Expression)):
        if isinstance(rhs, (VariableVector, VectorExpression, np.ndarray)):
            if isinstance(rhs, np.ndarray):
                raise_if_not_one_dim(rhs)
            return VectorExpression([lhs + rhs[i] for i in range(len(rhs))])

    if isinstance(lhs, (VariableVector, VectorExpression)):
        if isinstance(rhs, (VariableVector, VectorExpression, np.ndarray)):
            if isinstance(rhs, np.ndarray):
                raise_if_not_one_dim(rhs)
            if len(lhs) != len(rhs):
                raise ValueError(f"Cannot perform addition, length ({len(lhs)}) does not match length ({len(rhs)}).")
            return VectorExpression([lhs[i]+rhs[i] for i in range(len(rhs))])
        if is_numeric(rhs):
            return VectorExpression([lhs[i] + rhs for i in range(len(lhs))])

    return NotImplemented


def mul_dispatcher(
    lhs: Union[Expression, SubVariable, Term, VariableVector, VectorExpression],
    rhs: Union[np.ndarray, Expression, SubVariable, Term, VariableVector, VectorExpression]
) -> Union[Expression, Term, VectorExpression]:
    """multiply dispatch to the right operation"""
    if isinstance(lhs, SubVariable):
        if isinstance(rhs, SubVariable):
            return Term(lhs, rhs, 1)
        if isinstance(rhs, Term):
            if rhs.v2() is not None:
                raise ValueError(f"TitanQ only supports polynomials of maximum degree 2, the input expression has degree too hight")
            return Term(rhs.v1(), lhs, rhs.coeff())
        if is_numeric(rhs):
            return Term(lhs, None, rhs)

    if isinstance(lhs, Term):
        if isinstance(rhs, Term):
            if lhs.v2() is not None or rhs.v2() is not None:
                raise ValueError(f"TitanQ only supports polynomials of maximum degree 2, the input expression has degree too hight")
            return Term(lhs.v1(), rhs.v1(), lhs.coeff()*rhs.coeff())
        if is_numeric(rhs):
            return Term(lhs.v1(), lhs.v2(), lhs.coeff()*rhs)

    if isinstance(lhs, Expression):
        if isinstance(rhs, Expression):
            new_expr = Expression()
            for term in lhs.terms():
                new_expr += term * rhs
            return new_expr
        if is_numeric(rhs) or isinstance(rhs, (Term, SubVariable)):
            return Expression([term*rhs for term in lhs.terms()])

    if isinstance(lhs, (SubVariable, Term, Expression)):
        if isinstance(rhs, (VariableVector, VectorExpression, np.ndarray)):
            if isinstance(rhs, np.ndarray):
                raise_if_not_one_dim(rhs)
            return VectorExpression([lhs*rhs[i] for i in range(len(rhs))])

    if isinstance(lhs, VariableVector):
        if isinstance(rhs, (VariableVector, np.ndarray)):
            if isinstance(rhs, np.ndarray):
                raise_if_not_one_dim(rhs)
            if len(lhs) != len(rhs):
                raise ValueError(f"Cannot perform multiplication, length ({len(lhs)}) does not match length ({len(rhs)}).")
            return VectorExpression([Expression([lhs[i]*rhs[i]]) for i in range(len(lhs))])
        if is_numeric(rhs):
            return VectorExpression([Expression([lhs[i]*rhs]) for i in range(len(lhs))])

    if isinstance(lhs, VectorExpression):
        if isinstance(rhs, (VariableVector, np.ndarray, VectorExpression)):
            if isinstance(rhs, np.ndarray):
                raise_if_not_one_dim(rhs)
            if len(lhs) != len(rhs):
                raise ValueError(f"Cannot perform multiplication, length ({len(lhs)}) does not match length ({len(rhs)}).")
            return VectorExpression([lhs[i]*rhs[i] for i in range(len(lhs))])
        if is_numeric(rhs):
            return VectorExpression([lhs[i]*rhs for i in range(len(lhs))])

    return NotImplemented


def matmul_dispatcher(
    lhs: Union[np.ndarray, VariableVector, VectorExpression],
    rhs: Union[np.ndarray, VariableVector, VectorExpression]
) -> Expression:
    """dot product dispatch to the right operation"""
    if isinstance(lhs, (VariableVector, np.ndarray, VectorExpression)):
        if isinstance(rhs, (VariableVector, np.ndarray, VectorExpression)):
            if len(lhs) != len(rhs):
                raise ValueError(f"Cannot perform dot product, length ({len(lhs)}) does not match length ({len(rhs)}).")
            if (isinstance(lhs, np.ndarray) or isinstance(rhs, np.ndarray)) and rhs.ndim == 2:
                return VectorExpression([lhs@rhs.T[i] for i in range(len(rhs.T))])
            if isinstance(lhs, VectorExpression) or isinstance(rhs, VectorExpression):
                terms_list= []
                [terms_list.extend((lhs[i] * rhs[i]).terms()) for i in range(len(lhs))]
                return Expression(terms_list)
            return Expression([lhs[i] * rhs[i] for i in range(len(lhs))])

    return NotImplemented


def raise_if_not_one_dim(array: np.ndarray) -> None:
    """raise ValueError if the array is larger than one dimension"""
    if array.ndim != 1:
        raise ValueError(f"Expected a 1-dimensional array, but got an array with {array.ndim} dimensions.")


def is_numeric(value) -> bool:
    """return if the value is either a float, int, a numpy int or a numpy float"""
    return isinstance(value, (float, int, np.integer, np.floating))