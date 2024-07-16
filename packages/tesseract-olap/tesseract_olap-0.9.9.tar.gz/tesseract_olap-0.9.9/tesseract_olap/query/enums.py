from enum import Enum
from typing import Optional, Union

from typing_extensions import Literal


class Comparison(str, Enum):
    """Comparison Enum.

    Defines the available value comparison operations.
    """

    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"

    @classmethod
    def from_str(cls, value: str):
        value = value.strip().upper()
        try:
            return COMPARISON_SYMBOL.get(value) or cls[value]
        except KeyError:
            raise ValueError(f"Invalid Comparison value: {value}") from None


COMPARISON_SYMBOL = {
    ">": Comparison.GT,
    ">=": Comparison.GTE,
    "<": Comparison.LT,
    "<=": Comparison.LTE,
    "=": Comparison.EQ,
    "==": Comparison.EQ,
    "!=": Comparison.NEQ,
}


class Order(str, Enum):
    """Order direction Enum.

    Defines a direction to use in a sorting operation.
    """

    ASC = "asc"
    DESC = "desc"

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, value: Optional[str]):
        value = str(value).strip().upper()
        try:
            return cls[value]
        except KeyError:
            return cls.ASC


AnyOrder = Union[Literal["asc", "desc"], "Order"]


class Membership(Enum):
    """Membership Enum.

    Defines the membership of a value to a set."""

    IN = "in"
    NIN = "nin"

    @classmethod
    def from_str(cls, value: str):
        value = value.strip().upper()
        try:
            return cls[value]
        except KeyError:
            raise ValueError(f"Invalid Membership value: {value}") from None


class LogicOperator(str, Enum):
    """Logical connector Enum.

    Defines logical operations between conditional predicates.
    """

    AND = "and"
    OR = "or"
    XOR = "xor"

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, value: str):
        value = value.strip().upper()
        try:
            return cls[value]
        except KeyError:
            raise ValueError(f"Invalid LogicOperator value: {value}") from None


class RestrictionScale(str, Enum):
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, value: str):
        assert value, "Invalid RestrictionScale: no value provided"
        try:
            value = value.strip().upper()
            return cls[value]
        except KeyError:
            raise ValueError(f"Invalid RestrictionScale value: {value}") from None


class RestrictionAge(str, Enum):
    LATEST = "latest"
    OLDEST = "oldest"

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, value: str):
        assert value, "Invalid RestrictionAge: no value provided"
        try:
            value = value.strip().upper()
            return cls[value]
        except KeyError:
            raise ValueError(f"Invalid RestrictionAge value: {value}") from None
