# better-sum

[sum]: https://docs.python.org/3/library/functions.html#sum
[mkdocs]: https://www.mkdocs.org/
[typing-extensions]: https://pypi.org/project/typing-extensions/
[decorator]: docs/usage.md#decorator
[class attribute]: docs/usage.md#a-class-attribute

Python's [sum][], minus ugly annotations and extra arguments.

## Project goals

- [x] Prototype a cleaner [sum][]
- [x] Try [mkdocs][]

## Quickstart

1. Create a virtual environment with Python 3.9+
2. `pip install better-sum`
3. Try the code below

```python
from __future__ import annotations  # Allows forward references on Python < 3.11
from typing import NamedTuple
from better_sum import sum, sum_starts_at_instance


@sum_starts_at_instance(0.0, 0.0)  # 1. Create & store a default instance
class Vec2(NamedTuple):

    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: tuple[float, float]) -> Vec2:
        other_x, other_y = other
        return self.__class__(self.x + other_x, self.y + other_y)

    def __radd__(self, other: tuple[float, float]) -> Vec2:
        other_x, other_y = other
        return self.__class__(other_x + self.x, other_y + self.y)

 # 2. better_sum.sum automatically starts at the default instance
to_sum = [Vec2(0.0, 0.0), Vec2(1.0, 1.0), Vec2(2.0, 2.0)]
print(sum(to_sum))
```

As expected, this will print:
```
Vec(x=3.0, y=3.0)
```
[usage documentation]: https://better-sum.readthedocs.io/en/latest/usage.html

Learn more in the [usage documentation].

## What's wrong with Python's sum?

It complicates code.

```python
# The bad: verbose calls
sum(iterable, start_value)

# The ugly: gross type annotations
class SupportsSum:

    # int is ugly
    def __radd__(self, other: int | SupportsSum):
        if other == 0:
            return self
        ...
```

## What's the catch?

[pyglet]: https://pyglet.readthedocs.io/en/latest/

A potential speed hit from indirection.

If it's a concern, then one of two things is true:

1. You should be using binary-backed acceleration
2. You're writing code for one of the following:
   * [pyglet][] or another pure-Python project
   * fallback code for when binary acceleration isn't available
