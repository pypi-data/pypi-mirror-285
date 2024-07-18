from __future__ import annotations

from typing import TYPE_CHECKING, Any

SUPPORTED_UNDERSCORE_OPS_BINARY = set("+ - * / // % ** < <= > >= == != & | ^ << >>".split())
SUPPORTED_UNDERSCORE_OPS_UNARY = set("- + ~".split())


class Underscore:
    """An unevaluated underscore expression.

    Examples
    --------
    >>> class X:
    ...     y: DataFrame[Y] = has_many(...)
    ...     s: int = _.y[_.z].sum()
    """

    def __getattr__(self, attr: str) -> "Underscore":
        if attr.startswith("__") or attr.startswith("_chalk__"):
            raise AttributeError(f"{self.__class__.__name__!r} {attr!r}")
        return UnderscoreAttr(self, attr)

    def __getitem__(self, key: Any) -> "Underscore":
        return UnderscoreItem(self, key)

    def __call__(self, *args: Any, **kwargs: Any) -> "Underscore":
        return UnderscoreCall(self, *args, **kwargs)

    def __add__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("+", self, other)

    def __radd__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("+", other, self)

    def __sub__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("-", self, other)

    def __rsub__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("-", other, self)

    def __mul__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("*", self, other)

    def __rmul__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("*", other, self)

    def __truediv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("/", self, other)

    def __rtruediv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("/", other, self)

    def __floordiv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("//", self, other)

    def __rfloordiv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("//", other, self)

    def __mod__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("%", self, other)

    def __rmod__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("%", other, self)

    def __pow__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("**", self, other)

    def __rpow__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("**", other, self)

    def __lt__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<", self, other)

    def __le__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<=", self, other)

    def __gt__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">", self, other)

    def __ge__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">=", self, other)

    def __eq__(self, other: Any) -> "Underscore":  # pyright: ignore[reportIncompatibleMethodOverride]
        return UnderscoreBinaryOp("==", self, other)

    def __ne__(self, other: Any) -> "Underscore":  # pyright: ignore[reportIncompatibleMethodOverride]
        return UnderscoreBinaryOp("!=", self, other)

    def __and__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("&", self, other)

    def __rand__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("&", other, self)

    def __or__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("|", self, other)

    def __ror__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("|", other, self)

    def __xor__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("^", self, other)

    def __rxor__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("^", other, self)

    def __lshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<<", self, other)

    def __rlshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<<", other, self)

    def __rshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">>", self, other)

    def __rrshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">>", other, self)

    def __neg__(self) -> "Underscore":
        return UnderscoreUnaryOp("-", self)

    def __pos__(self) -> "Underscore":
        return UnderscoreUnaryOp("+", self)

    def __invert__(self) -> "Underscore":
        return UnderscoreUnaryOp("~", self)

    def __hash__(self):
        return hash(repr(self))

    if not TYPE_CHECKING:

        def if_then_else(self: Any, *args: Any, **kwargs: Any):
            """
            This function is used to provide a better error message for when it is accidentally
            called on a non-root underscore expression.

            This overload should not actually be called - call the method directly on `_` instead.
            """
            raise ValueError(
                f"You cannot call .if_then_else on expression '{repr(self)}'; call it on the root _ instead, as in '_.if_then_else(condition, if_true, if_false)'"
            )


class UnderscoreRoot(Underscore):
    # _
    def __repr__(self):
        return "_"

    def if_then_else(
        self,
        condition: Underscore,
        if_true: Any,
        if_false: Any,
    ) -> Underscore:
        """
        Create a conditional expression, roughly equivalent to
        ```
        if condition:
            return if_true
        else:
            return if_false
        ```

        Unlike a Python if/else, all three inputs (condition, if_true, if_false) are evaluated
        in parallel for all rows, and then the correct side is selected based on the result of
        the condition expression.
        """
        return UnderscoreIfThenElse(
            condition=condition,
            if_true=if_true,
            if_false=if_false,
        )


class UnderscoreAttr(Underscore):
    # _.a
    def __init__(self, parent: Underscore, attr: str):
        super().__init__()
        self._chalk__parent = parent
        self._chalk__attr = attr

    def __repr__(self):
        return f"{self._chalk__parent}.{self._chalk__attr}"


class UnderscoreItem(Underscore):
    # _[k]
    def __init__(self, parent: Underscore, key: Any):
        super().__init__()
        self._chalk__parent = parent
        self._chalk__key = key

    def __repr__(self):
        return f"{self._chalk__parent}[{self._chalk__key}]"


class UnderscoreCall(Underscore):
    # _(args, kwargs)
    def __init__(self, parent: Underscore, *args: Any, **kwargs: Any):
        super().__init__()
        self._chalk__parent = parent
        self._chalk__args = args
        self._chalk__kwargs = kwargs

    def __repr__(self):
        return f"{self._chalk__parent}(args: {self._chalk__args}, kwargs: {self._chalk__kwargs})"


class UnderscoreBinaryOp(Underscore):
    # _.a + _.b
    # _ and _.c
    def __init__(self, op: str, left: Any, right: Any):
        super().__init__()
        self._chalk__op = op
        self._chalk__left = left
        self._chalk__right = right

    def __repr__(self):
        return f"({self._chalk__left} {self._chalk__op} {self._chalk__right})"


class UnderscoreUnaryOp(Underscore):
    #!_.a
    def __init__(self, op: str, operand: Any):
        super().__init__()
        self._chalk__op = op
        self._chalk__operand = operand

    def __repr__(self):
        return f"{self._chalk__op}{self._chalk__operand}"


class UnderscoreIfThenElse(Underscore):
    # _.if_then_else(...)
    def __init__(
        self,
        condition: Underscore,
        if_true: Any,
        if_false: Any,
    ):
        super().__init__()
        if not isinstance(condition, Underscore):
            raise ValueError(
                f"The underscore expression .if_then_else() must be given an underscore expression as a condition, but was given '{repr(condition)}'"
            )
        self._chalk__condition = condition
        self._chalk__if_true = if_true
        self._chalk__if_false = if_false

    def __repr__(self):
        return f"_.if_then_else({self._chalk__condition}, {self._chalk__if_true}, {self._chalk__if_false})"


_ = underscore = UnderscoreRoot()


# NEED `__all__` because `_` is private and can't be auto-imported by i.e. IntelliJ.
__all__ = [
    "SUPPORTED_UNDERSCORE_OPS_BINARY",
    "SUPPORTED_UNDERSCORE_OPS_UNARY",
    "Underscore",
    "UnderscoreAttr",
    "UnderscoreCall",
    "UnderscoreItem",
    "UnderscoreBinaryOp",
    "UnderscoreUnaryOp",
    "UnderscoreRoot",
    "underscore",
    "_",
]
