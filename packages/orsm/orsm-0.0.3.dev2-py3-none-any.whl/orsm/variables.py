"""
Variable mangling.
"""


from varname.helpers import jsobj
from functools import wraps

def return_dict_items(func, *func_args, **func_kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Keywords specified in the function take precedence over those in the wrapper is they clash, so some might need to be dropped.
        _func_kwargs = func_kwargs
        for k in kwargs.keys():
            if k in _func_kwargs:
                _func_kwargs = {i:j for i,j in func_kwargs.items() if i != k}
        return func(*func_args, *args, **kwargs, **_func_kwargs).items()

    return wrapper


variable_names_and_objects = return_dict_items(jsobj, vars_only=False, frame=2)
