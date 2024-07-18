"""Python's sum, minus ugly annotations and extra arguments.

Unlike the current built-in version, this one allows per-type default
start values so you don't have to pollute `__radd__` by accepting `0`.
"""
from __future__ import annotations
from typing import Type, TypeVar, Iterable, overload, Callable, Final, Protocol


try:
    from typing_extensions import Self
except ImportError:
    from typing_extensions import Self
try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec


_SUM_SIGNAL_CLASS_ATTR: Final[str] = '__sum_starts__'


# Used to set up the _HasAdd Protocol + a few other annotations below
_T = TypeVar('_T')
_T_co = TypeVar('_T_co', covariant=True)
_T_contra = TypeVar('_T_contra', contravariant=True)


class _HasAdd(Protocol[_T_contra, _T_co]):
    """We only need __add__ since user-provided objects have __radd__."""

    def __add__(self, __a: _T_contra) -> _T_co: ...


# Adding-related types
_A = TypeVar('_A', bound=_HasAdd)
_SumResult = TypeVar('_SumResult', bound=_HasAdd)  # Result sum type
_SummableInstanceParams = ParamSpec('_SummableInstanceParams')


class _SumFunc(Protocol[_A, _SumResult]):
    """Annotates [`sum`][better_sum.sum] as a Protocol type annotation.

    This is an attempt to cover variadic callables on Python <= 3.9
    well enough to pass pyright's type checking. Although this is
    cobbled together from builtins.pyi and Protocol:

    * It probably works on Python 3.8
    * It will hold things over until typing improvements from
      later Python versions becomes generally available instead
      of the weak typing-extensions versions

    """

    @overload
    def __call__(self, __iterable: Iterable[_SumResult]) -> _A | int:
        ...

    @overload
    def __call__(self, __iterable: Iterable[_A], __start: _SumResult | int) -> _SumResult:
        ...

    def __call__(self, *args) -> _A | int | _SumResult:
        ...


# Preserve this for later use since we'll need it
_builtin_sum: Final[_SumFunc] = sum


# Although pyright claims the line below is meaningless, it
# expresses the idea of mapping a type to an instance of it
_sum_start_defaults: dict[Type[_T], _T] = {}  # type: ignore


def sum_starts_at_instance(
    *args: _SummableInstanceParams.args,  # type: ignore
    **kwargs: _SummableInstanceParams.kwargs
) -> Callable[[Type[_T]], Type[_T]]:
    """Register a type's start value for [sum][better_sum.sum].

    Args:
        args:
            Pass arguments as specified in the decorated type's positional arguments.
            Mutually exclusive with `with_args`
        kwargs:
            Any keyword arguments as specified by the decorated type.
    """
    def _registering_func(wrapped_class: Type[_T]) -> Type[_T]:
        _sum_start_defaults[wrapped_class] = wrapped_class(*args, **kwargs)
        return wrapped_class

    return _registering_func


@overload
def sum(__iterable: Iterable[_A]) -> _A | int:
    ...


@overload
def sum(__iterable: Iterable[_A], __start: _SumResult) -> _A | _SumResult:
    ...


def sum(__iterable: Iterable[_A], *maybe_start):
    """A type-aware extension replacing Python's built-in [sum][].

    To use it, first register types by doing one of the following:

    1. Use the [sum_starts_at_instance][better_sum.sum_starts_at_instance]
       decorator
    2. Provide a `__sum_start__` class attribute on a type

    Both of these can get tricky, but the decorator is probably easier.

    Python's built-in [sum][] usually starts the accumulator value
    at `0`, but you can set it to anything you want with via its optional
    positional `start` argument.

    Args:
        __iterable: An iterable to sum the contents of.
        __start: An optional overriding start value, just as in the
            original sum.
    """
    maybe_start_len = len(maybe_start)
    if maybe_start_len == 1:
        return _builtin_sum(__iterable, maybe_start[0])
    elif maybe_start_len > 1:
        raise TypeError("sum takes an iterable and an optional start argument")

    nonexhaustion_wrapper = iter(__iterable)
    first = next(nonexhaustion_wrapper)
    first_type = type(first)

    # It's been added via the decorator args
    if first_type in _sum_start_defaults:
        start: _A = \
            _sum_start_defaults[first_type] + first  # type: ignore

    # The class has a sum signal class attribute
    elif hasattr(first_type, _SUM_SIGNAL_CLASS_ATTR):
        start = getattr(first_type, _SUM_SIGNAL_CLASS_ATTR) + first

    # It's an ordinary boring class, so fall back to classic behavior
    else:
        # TODO: check if this is a pyright bug (0 has __add__?)
        start = 0  # type: ignore

    return _builtin_sum(nonexhaustion_wrapper, start)
