#!/usr/bin/env python3
"""
Handling arguments.
"""

import itertools
from orsm.variables import variable_names_and_objects


def all_combinations(iterable, *, min_length=None, max_length=None):
    """
    Determines the possible combinations that can be formed from an iterable,
    where 0 items are selected, 1 item is selected, 2 items are selected, ...,
    until all the items are selected.
    e.g. [a,b,c] produces:
    [(),
     ('a',),
     ('b',),
     ('c',),
     ('a', 'b'),
     ('a', 'c'),
     ('b', 'c'),
     ('a', 'b', 'c')]
    """
    for variable, value in variable_names_and_objects(max_length, min_length):
        if value is not None:
            assert isinstance(value, int) and value >= 0, f"The {variable = } needs to be a positive integer, not {value = }"
    if all([i is not None for i in [min_length, max_length]]):
        assert min_length <= max_length, f"The bounding lengths contradict: {max_length = } and {min_length = }"
    size = 0
    reached_max_size = False

    while (max_length is not None and size <= max_length) or (max_length is None and not reached_max_size):
        if max_length is None:
            # We will have to determine when to stop
            iterable_size = len(iterable)
            reached_max_size = (size == iterable_size)
        if min_length is None or size >= min_length:
            yield from itertools.combinations(iterable, size)
        size += 1


def all_kwarg_combinations(*, keys, values, min_length=None, max_length=None):
    """
    For a list of keys [a, b] and values [1, 2] it produces
    all the unique combinations of key-value pairings:
    [{},
     {'a': 1},
     {'a': 2},
     {'b': 1},
     {'b': 2},
     {'a': 1, 'b': 1},
     {'a': 1, 'b': 2},
     {'a': 2, 'b': 1},
     {'a': 2, 'b': 2}]

    This is quite useful in unit tests for combinations of possible
    arguments.
    """
    individual_pairings = [list(itertools.product([key], values)) for key in keys]
    combinations = all_combinations(individual_pairings, min_length=min_length, max_length=max_length)
    yield from (dict(kwarg) for combination in combinations for kwarg in itertools.product(*combination))
