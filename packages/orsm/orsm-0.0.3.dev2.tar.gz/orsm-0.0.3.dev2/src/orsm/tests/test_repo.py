#!/usr/bin/env python3
import unittest
from orsm.variables import variable_names_and_objects
from orsm import repo


class VersionInfo(unittest.TestCase):

    def test_basic_repo_info(self):
        for variable, get_string_function in variable_names_and_objects(repo.repo_name, repo.repo_author, repo.repo_version, repo.repo_email):
            output = get_string_function()
            self.assertIsInstance(output, str, msg=f"The {variable = } with {output = } is not the right type.")
            self.assertTrue(output, msg=f"The {variable = } with {output = } is meant to be non-trivial.")


if __name__ == '__main__':
    unittest.main()
