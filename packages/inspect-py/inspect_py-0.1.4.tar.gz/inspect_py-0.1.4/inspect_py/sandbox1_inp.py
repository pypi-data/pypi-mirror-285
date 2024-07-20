from inspect_py.utils_inp import *
from typing import *
from pathlib import Path

def assert_message(actual:Any,expect:Any, verbose:int = 0) -> str:
    # not done with list

    # done with list and Scalar but haven't tested

    import numpy as np
    Scalar_Numpy = Union[np.number, np.bool_, np.object_, np.string_]
    Scalar_BuiltIn = Union[int, float, str, bool, np.number, np.bool_]
    Scalar = Union[Scalar_BuiltIn,Scalar_Numpy]
    
    
    if type(actual) != type(expect):
        out_str = f"The type of actual is {type(actual)} while the correct type is {type(expect)}"
        return out_str
    else:
        if isinstance(actual, Scalar):
            out_str = f"The actual is {actual} while the correct would be {expect}\n"
        elif isinstance(actual, list):
            if len(actual) != len(expect):
                out_str = f"The length of actual is {len(actual)} while it's expected to have the length of {len(expect)}\n"
            only_in_actual = [x for x in actual if x not in expect]
            only_in_expect = [x for x in expect if x not in actual]
            # already correct list
            if len(only_in_actual) == 0 and len(only_in_expect) == 0:
                return ""
            out_str += f"these items are only in actual {only_in_actual}\n"
            out_str += f"these items are only in expect {only_in_expect}\n"
        elif isinstance(actual, dict):
            if len(actual) != len(expect):
                out_str = f"The length of actual is {len(actual)} while it's expected to have the length of {len(expect)}\n"
            key_actual = list(actual.keys())
            key_expect = list(expect.keys())
            
            for key, value in actual.items():
                expect_value = expect[key]
                curr_str = f"At key {key} the value of actual is {value} but the correct value is {expect_value}\n"
                out_str += curr_str
        elif issubclass(actual, Exception):
            # check error type
            # correct type
            if isinstance(actual, expect):
                return ""
            else:
                out_str = f"The error of actual is {actual} while the correct error should be {expect}\n"
            pass
        
        if verbose >= 1:
            print(out_str)
        return out_str

def get_builtin_func():
    import builtins
    all_builtin_functions = [name for name in dir(builtins) if callable(getattr(builtins, name))]
    return all_builtin_functions

def input_params(function):
    import inspect
    """
    Returns a list of parameter names for the given function.
    """
    signature = inspect.signature(function)
    out_list = [param.name for param in signature.parameters.values()]
    return out_list

def get_fun_names(py_code_path: Union[str,Path]):
    """
    Analyzes a Python file and returns a list of function names defined in the file.

    Parameters
    ----------
    py_code_path : str
        The path of the Python file (.py) to analyze.

    Returns
    -------
    list of str
        A list containing the names of functions defined in the file.
    """
    import ast

    with open(str(py_code_path), "r") as file:
        tree = ast.parse(file.read(), filename=str(py_code_path))

    function_names = []

    class FunctionVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            function_names.append(node.name)
            self.generic_visit(node)
    
    visitor = FunctionVisitor()
    visitor.visit(tree)

    return function_names

# Example usage
# functions = get_fun_names('path_to_your_python_file.py')
# print(functions)


