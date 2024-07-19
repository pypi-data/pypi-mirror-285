from pathlib import Path
from operator import itemgetter
import re

from .config import (
    ALTER_MODULE,
    ALTER_TYPE,
    FIELDS,
    IMPORTS,
    CLASSES,
    DISABLE_OUTPUT_DIR,
    DTO_TEMPLATE,
)
from .utils import (
    dynamic_import,
    inspect_function,
    snake_to_class,
    find_files,
    extract_data_from_file,
)


def extract_fields_from_func(func: callable, exclude=set()):
    """
    Extracts fields from a function's signature and alters their types if necessary.

    Args:
        func: The function to inspect.
        exclude: Set of field names to exclude.

    Returns:
        Tuple containing a list of fields and the return type.
    """
    fields = []
    return_type, args = inspect_function(func)
    for field_name, type_as_string in args:
        if field_name in exclude:
            continue
        for key, value in ALTER_TYPE.items():
            if key in type_as_string:
                type_as_string = type_as_string.replace(key, value)
        fields.append({"name": field_name, "type": type_as_string})
    return fields, return_type


def construct_imports(imports: set, exclude=set()):
    """
    Constructs import statements from a set of imports, excluding specified modules.

    Args:
        imports: Set of import strings.
        exclude: Set of imports to exclude.

    Returns:
        A string containing import statements.
    """
    imports = imports.difference(exclude)
    from_imports_dic = {}
    normal_imports = []
    while imports:
        import_string = imports.pop()
        import_string = ALTER_MODULE.get(import_string, import_string)
        imports_list = import_string.split(".")

        to_import = imports_list.pop()
        module = ".".join(imports_list)

        if to_import in exclude or module in exclude:
            continue

        if module:
            from_imports_dic[module] = from_imports_dic.get(module, []) + [to_import]
        else:
            normal_imports.append(f"import {to_import}\n")

    from_imports_list = [
        f"from {module} import {', '.join(to_imports)}\n"
        for module, to_imports in sorted(from_imports_dic.items(), key=itemgetter(0))
    ]

    return "".join(normal_imports) + "\n" + "".join(from_imports_list)


def generate_dtos(
    source_directory: str | Path = ".",
    output_directory: str | Path = None,
    init_file: bool = True,
):
    """
    Generates DTO classes from EdgeQL files in the specified source directory.

    Args:
        source_directory: Directory containing EdgeQL files.
        output_directory: Directory to output generated DTO files.
        init_file: Whether to create __init__.py files in output directories.
    """
    source_directory = Path(source_directory)
    specified_output = output_directory is not None and not DISABLE_OUTPUT_DIR

    edgeql_files = find_files(source_directory, "_edgeql.py")
    dto_files = {}

    for file in edgeql_files:
        file = Path(file)
        pure_name = file.stem.replace("_edgeql", "")
        class_name = snake_to_class(pure_name)
        sync = "async" not in pure_name
        function_name = pure_name.replace("_async", "")
        dto_file_path = Path(f"{file.stem}_dto.py")

        imports, classes = extract_data_from_file(file)
        imports = imports.union(IMPORTS["include"]).difference(IMPORTS["exclude"])
        classes = classes.union(CLASSES["include"]).difference(CLASSES["exclude"])

        if specified_output:
            output_directory = Path(output_directory)
        else:
            output_directory = file.parent / "dto"

            while classes:
                imports.add(f"..{file.stem}.{classes.pop()}")

            imports.add(f"..{file.stem}.{function_name}")

        output_directory.mkdir(parents=True, exist_ok=True)
        import_string = construct_imports(imports)

        generated_function = dynamic_import(file.absolute(), function_name)
        fields, return_type = extract_fields_from_func(
            generated_function, FIELDS["exclude"]
        )

        with_default = []
        rest = []
        for field in fields:
            if "None" in field["type"]:
                field["type"] += " = None"
                with_default.append(field)
            else:
                for default in FIELDS["defaults"]:
                    matched = re.match(default["pattern"], field["type"], re.IGNORECASE)
                    if matched:
                        field["type"] += default["default"]
                        with_default.append(field)
                        break
                if not matched:
                    rest.append(field)

        fields = rest + with_default

        rendered_template = DTO_TEMPLATE.render(
            specified_output=specified_output,
            import_string=import_string,
            fields=fields,
            classes=classes,
            class_name=class_name,
            function_name=function_name,
            return_type=return_type,
            function_path=file.absolute(),
            sync=sync,
        )

        output_file_path = output_directory / dto_file_path
        if init_file:
            dto_files[output_directory] = dto_files.get(output_directory, []) + [
                {
                    "filename": dto_file_path.stem,
                    "classname": class_name,
                }
            ]
        output_file_path.write_text(rendered_template)

    for output_dir in dto_files.keys():
        init_file = Path(output_dir / "__init__.py")
        init_content = (
            "\n".join(
                [
                    f"from .{file['filename']} import {file['classname']}"
                    for file in dto_files[output_dir]
                ]
            )
            + "\n"
        )
        init_file.write_text(init_content)
