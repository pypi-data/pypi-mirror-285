#!/usr/bin/env python3
import unittest
from orsm.variables import variable_names_and_objects


class TestVariableNamesAndObjects(unittest.TestCase):
    def test_plain_variables(self):
        values = [1, 2, 3]
        a, b, c = values
        names = list("abc")
        for i, [name, variable] in enumerate(variable_names_and_objects(a, b, c)):
            self.assertEqual(name, names[i])
            self.assertEqual(variable, values[i])

    # @unittest.skipIf(True, reason="Awaiting a resolution of issue before we define the desired behaviour: https://github.com/pwwang/python-varname/issues/110")
    def test_compound_variables(self):
        class A:
            ...

        A.b = 1
        for i, [name, variable] in enumerate(variable_names_and_objects(A.b, vars_only=False)):
            self.assertEqual(name, "A.b")
            self.assertEqual(variable, 1)
        for i, [name, variable] in enumerate(variable_names_and_objects(A.b)):
            self.assertEqual(name, "A.b")
            self.assertEqual(variable, 1)

    def test_compound_variables_disabled(self):
        class A:
            ...

        A.b = 1
        for i, [name, variable] in enumerate(variable_names_and_objects(A.b, vars_only=True)):
            self.assertEqual(name, "b")
            self.assertEqual(variable, 1)


    def test_import_variable(self):
        from variables_foo import bar as _bar
        self.assertEqual("_bar", next(iter(variable_names_and_objects(_bar)))[0])

    def test_import_function(self):
        from variables_foo import baz as _baz
        self.assertEqual("_baz", next(iter(variable_names_and_objects(_baz)))[0])

    def test_import_class(self):
        from variables_foo import qux as _qux
        self.assertEqual("_qux", next(iter(variable_names_and_objects(_qux)))[0])


if __name__ == '__main__':
    unittest.main()
