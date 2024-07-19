#!/usr/bin/env python3

import sys

print(sys.path)

import unittest
import time
from orsm.timing import time_function, Timeout, TimeoutError
from orsm.arguments import all_kwarg_combinations


class TimeoutHandler(unittest.TestCase):

    def test_raises_error(self):
        with self.assertRaises(TimeoutError):
            with Timeout(timeout=1):
                time.sleep(2)

    def test_bad_values(self):
        for value in [-1, 0, Timeout.max_limit + 1]:
            with self.assertRaises(AssertionError):
                Timeout(timeout=value)

    def test_allowed_values(self):
        for value in [-1, Timeout.max_limit + 1]:
            with self.assertRaises(AssertionError):
                Timeout(timeout=value)


class TimingFunction(unittest.TestCase):

    def setUp(self):
        self.function = time.sleep
        self.name = "sleep test"
        self.duration = 0.3
        self.iter_limit = 3
        self.time_limit = 5
        self.expected = {"name": self.name, "seconds": 3, "total_iterations": 3, "average": self.duration}

    def test_return_type(self):
        with Timeout(timeout=10):
            results = time_function(self.duration, name=self.name, function=self.function, iter_limit=self.iter_limit, time_limit=self.time_limit)
            for key, value in results.items():
                self.assertIn(key, self.expected.keys())

    def test_return_values_seem_sensible(self):
        with Timeout(timeout=10):
            results = time_function(self.duration, name=self.name, function=self.function, iter_limit=self.iter_limit, time_limit=self.time_limit)
            self.assertEqual(results["name"], self.expected["name"])
            self.assertEqual(results["total_iterations"], self.expected["total_iterations"])
            self.assertAlmostEqual(results["average"], self.expected["average"], 1)

    def test_assertions(self):
        for kwargs in all_kwarg_combinations(keys=["iter_limit", "time_limit"], values=[0, -1]):
            with self.assertRaises(AssertionError, msg=f"The failing arguments are {kwargs = }"):
                time_function(self.duration, name=self.name, function=self.function, **kwargs)


if __name__ == '__main__':
    unittest.main()
