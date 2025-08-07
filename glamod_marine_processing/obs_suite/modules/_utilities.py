"""Module containing utility decorators."""

from __future__ import annotations

import builtins
import inspect


def auto_cast(func):
    """
    A decorator that automatically casts function arguments to the types specified
    in the function's type annotations.

    This is useful when you want to ensure that inputs conform to expected types
    without manually converting them inside the function body.

    Raises
    ------
    TypeError
        If the type conversion is not possible.
    ValueError
        If an argument cannot be converted to the specified type.

    Examples
    --------
    >>> @auto_cast
    ... def test_func(value: int):
    ...     print(type(value), value)
    >>> test_func("10")  # Will convert "10" (str) to 10 (int)

    Limitations
    -----------
        - Only works with basic type annotations (e.g., int, float, str).
        - Does not handle complex annotations like List[int], Optional[str], etc.
    """

    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            expected_type = sig.parameters[name].annotation
            expected_type = getattr(builtins, expected_type, None)

            if expected_type is None:
                continue
            if isinstance(value, expected_type):
                continue
            try:
                bound.arguments[name] = expected_type(value)
            except TypeError:
                raise TypeError(
                    f"Type conversion from {value} to {expected_type} is not possible."
                )
            except ValueError:
                raise ValueError(
                    f"Cannot convert {value} to specific type {expected_type}."
                )

        return func(*bound.args, **bound.kwargs)

    return wrapper
