#!/usr/bin/env python3
"""
Some basic profiling tools.

This is largely copied from: https://medium.com/uncountable-engineering/pythons-line-profiler-32df2b07b290
"""

from line_profiler import LineProfiler
from functools import wraps
import inspect
from orsm.logger import log as logging
from orsm import cli
import atexit
import tracemalloc
from orsm.decorators import disable_decorator


def is_in_debugger():
    # Taken from https://stackoverflow.com/a/338391/5134817
    for frame in inspect.stack():
        if frame[1].endswith("pydevd.py"):
            return True
    return False


time_profiler = LineProfiler()


@disable_decorator(cli.profiling_disabled, reason="Profiling has not been enabled from the command line.")
@disable_decorator(is_in_debugger, reason="Time profiling disabled in debug mode.")  # The debugger used in e.g. Pycharm requires sys.settrace (cf. https://github.com/pyutils/line_profiler/issues/276), but that's what LineProfiler uses and it upsets everything, so we disable this in debug mode.
def profile_time(func):
    @wraps(func)
    def profiled_function(*args, **kwargs):
        time_profiler.add_function(func)
        time_profiler.enable_by_count()
        return func(*args, **kwargs)

    return profiled_function


class MemoryProfiler:

    def __init__(self):
        self.max_usages = {}

    def store(self, *, name, peak):
        self.max_usages[name] = max(peak, self.max_usages[name]) if name in self.max_usages else peak

    def print_stats(self):
        print(f"\n\nMemory Usage\n" + "=" * 80)
        for name, peak in sorted(self.max_usages.items(), key=lambda i: i[1]):
            print(f"Maximal memory usage for {name}: Peak={peak / 10 ** 6}MB")


memory_profiler = MemoryProfiler()


@disable_decorator(cli.profiling_disabled, reason="Profiling has not been enabled from the command line.")
def profile_memory(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        logging.debug(f'Memory usage for {func.__name__}: Current={current / 10 ** 6}MB, Peak={peak / 10 ** 6}MB')
        memory_profiler.store(name=func.__name__, peak=peak)
        return result

    return wrapper


@atexit.register
def print_profilers():
    if not cli.profiling_disabled():
        time_profiler.print_stats(output_unit=1e-3)
        memory_profiler.print_stats()


if __name__ == "__main__":
    parser = cli.setup_standard_parser()
    parser.parse_args(["--profiling"])


    @profile_memory
    @profile_time
    def some_example():
        import time
        for i in range(5):
            time.sleep(0.1)


    some_example()
