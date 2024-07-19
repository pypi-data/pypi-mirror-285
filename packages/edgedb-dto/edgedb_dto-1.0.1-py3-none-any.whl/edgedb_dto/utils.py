from inspect import signature
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import sys
import ast
import os
from types import ModuleType


def find_files(directory: str | Path, extension=""):
    """
    Recursively searches for files with a specific extension in the specified directory and its subdirectories.

    Args:
        directory: The directory to search within.
        extension: The file extension to look for.

    Returns:
        A list of paths to files with the specified extension.
    """
    edgeql_files = []
    directory = Path(directory)

    assert directory.is_dir(), "The specified directory does not exist."

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                edgeql_files.append(os.path.join(root, file))

    return edgeql_files


def extract_data_from_file(file_path: str | Path):
    """
    Extracts import statements and class definitions from a Python file.

    Args:
        file_path: Path to the Python file.

    Returns:
        A tuple containing sets of imports and class names.
    """
    file_path = Path(file_path)

    assert file_path.is_file(), "The specified file does not exist."

    with file_path.open("r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    imports = set()
    classes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        if isinstance(node, ast.ClassDef):
            classes.add(node.name)

    return imports, classes


def snake_to_class(snake_case: str):
    """
    Converts a snake_case string to CamelCase.

    Args:
        snake_case: The snake_case string.

    Returns:
        The CamelCase string.
    """
    words = snake_case.split("_")
    class_case = "".join(word.title() for word in words)
    return class_case


def dynamic_import(module: str | Path | ModuleType, to_import: str):
    """
    Dynamically imports during runtime an attribute from a module.

    Args:
        module: The module or its path.
        to_import: The attribute to import.

    Returns:
        The imported attribute.

    Raises:
        AttributeError: If the attribute does not exist in the module.
    """
    if not isinstance(module, ModuleType):
        module = module_import(module)
    if hasattr(module, to_import):
        return getattr(module, to_import)
    else:
        raise AttributeError(f"The {to_import} does not exist in the module.")


def module_import(abs_path: str | Path):
    """
    Imports a module from a specified file path.

    Args:
        abs_path: The absolute path to the module file.

    Returns:
        The imported module.
    """
    abs_path = Path(abs_path)
    spec = spec_from_file_location("module.name", abs_path)
    module = module_from_spec(spec)
    sys.modules["module.name"] = module
    spec.loader.exec_module(module)
    return module


def inspect_function(func: callable):
    """
    Inspects a function and returns its return type and parameters.

    Args:
        func: The function to inspect.

    Returns:
        A tuple containing the return type and a list of parameter name-type pairs.
    """
    sig = signature(func)
    return sig.return_annotation, [
        (name, param.annotation) for name, param in sig.parameters.items()
    ]


def clean_dictionary(data: dict):
    """
    Cleans a dictionary by removing key-value pairs where the value is None.

    Args:
        data: The dictionary to be cleaned.

    Returns:
        The cleaned dictionary.
    """
    return {k: v for k, v in data.items() if v is not None}


def unify_dict_to_func(data: dict, func: callable):
    """
    Unifies a dictionary with the parameters of a function, removing keys that do not match the function's parameters
    and adding missing parameters with a value of None.

    Args:
        data: The dictionary to unify.
        func: The function whose parameters will be used for unification.

    Returns:
        The unified dictionary.
    """
    sig = signature(func)
    valid_params = set(sig.parameters.keys())
    return unify_dict_to_keys(data, valid_params)


def unify_dict_to_keys(data: dict, keys: list[str]):
    """
    Creates a new dictionary containing only the specified keys from the given data dictionary.
    If a key is not present in the data dictionary, it will be added with a value of None.

    Args:
        data: The original dictionary.
        keys: The list of keys to include in the new dictionary.

    Returns:
        The new dictionary with specified keys.
    """
    result = {}
    for key in keys:
        result[key] = data.get(key, None)
    return result
