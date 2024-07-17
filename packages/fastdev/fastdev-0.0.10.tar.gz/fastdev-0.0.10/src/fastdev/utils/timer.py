from __future__ import annotations

from contextlib import ContextDecorator
from time import perf_counter

from fastdev.utils.tui import console


class Timer(ContextDecorator):
    """
    Measure the time of a block of code.

    Args:
        print_tmpl (str, optional): The template to print the time. Defaults to None. Can be a
             string with a placeholder for the time, e.g., "func foo costs {:.5f} s" or a
             string without a placeholder, e.g., "func foo".

    Examples:
        >>> # doctest: +SKIP
        >>> with timeit():
        ...     time.sleep(1)
        it costs 1.00000 s
        >>> @timeit("func foo")
        ... def foo():
        ...     time.sleep(1)
        func foo costs 1.00000 s
    """

    def __init__(self, print_tmpl: str | None = None):
        if print_tmpl is None:
            print_tmpl = "it costs {:.5f} s"

        if "{" not in print_tmpl and "}" not in print_tmpl:  # no placeholder
            print_tmpl = print_tmpl + " costs {:.5f} s"

        self._print_tmpl: str = print_tmpl
        self._start_time: float

    def __enter__(self):
        self._start_time = perf_counter()

    def __exit__(self, exec_type, exec_value, traceback):
        console.log(self._print_tmpl.format(perf_counter() - self._start_time))


__all__ = ["Timer"]
