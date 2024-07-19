"""
Variable mangling.
"""

from varname import argname

def variable_names_and_objects(*variables):
    """
    Takes the variables input to a function and returns a dict of
    their names and the underlying objects.

    This is ideal for iterating through a list of variables and
    keeping their names:
    e.g.

    a,b,c = 1,2,3
    for name, variable in get_variable_names_and_objects(a,b,c):
        print(name, variable)

    returns:

    a, 1
    b, 2
    c, 3

    This is particularly useful when a function or class has been
    renamed on an import to a new variable:
    e.g.

    from foo import bar as baz

    the __name__ of baz is still bar, and this function resolves that.
    """
    names = argname('variables')
    return dict(zip(names, variables)).items()