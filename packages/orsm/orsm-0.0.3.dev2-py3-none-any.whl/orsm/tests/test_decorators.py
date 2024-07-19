#!/usr/bin/env python3
import unittest

from orsm.decorators import disable_decorator, null_decorator
from functools import wraps


class Predicate:
    def __init__(self):
        self.value = None

    def __call__(self, *args, **kwargs):
        return self.value


predicate = Predicate()


def base_decorator(func):
    """Some simple decorator that has some side effect, such as e.g. doubling the result."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return 2.0 * func(*args, **kwargs)

    return wrapper


class TestDecoratorDisabler(unittest.TestCase):

    def setUp(self):
        def example_function(*args, **kwargs):
            return 1

        self.undecorated = example_function()
        self.decorated = base_decorator(example_function)()
        self.example_function = example_function

    def test_do_nothing(self):
        decorator = null_decorator(base_decorator)
        f = decorator(self.example_function)
        self.assertEqual(self.decorated, f())

    def test_never_disabled(self):
        decorator = disable_decorator(False, reason="Trying to enable")(base_decorator)
        f = decorator(self.example_function)
        self.assertEqual(self.decorated, f())

    def test_always_disabled(self):
        decorator = disable_decorator(True, reason="Trying to disable")(base_decorator)
        f = decorator(self.example_function)
        self.assertEqual(self.undecorated, f())

    def test_conditionally_disabled(self):
        decorator = disable_decorator(predicate, reason="Trying to conditionally disable")(base_decorator)
        f = decorator(self.example_function)
        predicate.value = True
        self.assertEqual(self.undecorated, f())
        predicate.value = False
        self.assertEqual(self.decorated, f())


if __name__ == "__main__":
    unittest.main()
