#!/usr/bin/env python3

import sys

print(sys.path)

import unittest
from orsm.arguments import all_combinations, all_kwarg_combinations


class Combinations(unittest.TestCase):
    def test_all_combinations(self):
        iterable = ["foo", "bar", "bax"]
        self.assertEqual(list(all_combinations(iterable)), [(), ("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax"), ("foo", "bar", "bax")])
        self.assertEqual(list(all_combinations(iterable, min_length=0)), [(), ("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax"), ("foo", "bar", "bax")])
        self.assertEqual(list(all_combinations(iterable, max_length=3)), [(), ("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax"), ("foo", "bar", "bax")])
        self.assertEqual(list(all_combinations(iterable, min_length=0, max_length=3)), [(), ("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax"), ("foo", "bar", "bax")])
        self.assertEqual(list(all_combinations(iterable, max_length=1)), [(), ("foo",), ("bar",), ("bax",)])
        self.assertEqual(list(all_combinations(iterable, min_length=1)), [("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax"), ("foo", "bar", "bax")])
        self.assertEqual(list(all_combinations(iterable, min_length=1, max_length=2)), [("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax")])
        self.assertEqual(list(all_combinations(iterable, max_length=4)), [(), ("foo",), ("bar",), ("bax",), ("foo", "bar"), ("foo", "bax"), ("bar", "bax"), ("foo", "bar", "bax")])

    def test_all_kwarg_combinations(self):
        values = ["foo", "bar"]
        keys = ["xxx", "yyy"]
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values)), [{}, {'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}, {'xxx': 'foo', 'yyy': 'foo'}, {'xxx': 'foo', 'yyy': 'bar'}, {'xxx': 'bar', 'yyy': 'foo'}, {'xxx': 'bar', 'yyy': 'bar'}])
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values, max_length=2)), [{}, {'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}, {'xxx': 'foo', 'yyy': 'foo'}, {'xxx': 'foo', 'yyy': 'bar'}, {'xxx': 'bar', 'yyy': 'foo'}, {'xxx': 'bar', 'yyy': 'bar'}])
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values, max_length=4)), [{}, {'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}, {'xxx': 'foo', 'yyy': 'foo'}, {'xxx': 'foo', 'yyy': 'bar'}, {'xxx': 'bar', 'yyy': 'foo'}, {'xxx': 'bar', 'yyy': 'bar'}])
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values, min_length=0)), [{}, {'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}, {'xxx': 'foo', 'yyy': 'foo'}, {'xxx': 'foo', 'yyy': 'bar'}, {'xxx': 'bar', 'yyy': 'foo'}, {'xxx': 'bar', 'yyy': 'bar'}])
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values, min_length=0, max_length=2)), [{}, {'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}, {'xxx': 'foo', 'yyy': 'foo'}, {'xxx': 'foo', 'yyy': 'bar'}, {'xxx': 'bar', 'yyy': 'foo'}, {'xxx': 'bar', 'yyy': 'bar'}])
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values, min_length=1)), [{'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}, {'xxx': 'foo', 'yyy': 'foo'}, {'xxx': 'foo', 'yyy': 'bar'}, {'xxx': 'bar', 'yyy': 'foo'}, {'xxx': 'bar', 'yyy': 'bar'}])
        self.assertEqual(list(all_kwarg_combinations(keys=keys, values=values, min_length=1, max_length=1)), [{'xxx': 'foo'}, {'xxx': 'bar'}, {'yyy': 'foo'}, {'yyy': 'bar'}])


if __name__ == '__main__':
    unittest.main()
