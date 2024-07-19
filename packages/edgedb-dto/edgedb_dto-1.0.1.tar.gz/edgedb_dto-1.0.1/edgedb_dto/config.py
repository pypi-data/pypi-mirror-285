from jinja2 import Template

# Maps types to their altered representations in DTOs
ALTER_TYPE = {
    "uuid.UUID": "DTO | uuid.UUID",
}

# Specifies modules to include or exclude during import generation
IMPORTS = {
    "exclude": {"edgedb", "__future__"},
    "include": {
        "edgedb_dto.dynamic_import",
        "edgedb_dto.module_import",
        "edgedb_dto.DTO",
        "dataclasses.field",
        "edgedb.AsyncIOClient",
        "edgedb.Client",
    },
}

# Specifies classes to include or exclude during DTO generation
CLASSES = {
    "exclude": {"NoPydanticValidation"},
    "include": {},
}

# Flag to disable output directory specification
DISABLE_OUTPUT_DIR = True

# Maps modules to their altered representations in DTOs
ALTER_MODULE = {"dataclasses": "pydantic.dataclasses.dataclass"}

# Specifies class fields to include or exclude, and their default values
FIELDS = {
    "exclude": {"executor"},
    "include": {},
    "defaults": [
        {"pattern": "list\[(.+)\]", "default": " = field(default_factory=list)"},
        {"pattern": "set\[(.+)\]", "default": " = field(default_factory=set)"},
    ],
}

# Jinja2 template for generating DTO classes
DTO_TEMPLATE = Template(
    """{{import_string}}

{% if specified_output%}
    FILE_PATH = "{{function_path}}"
    MODULE = module_import(FILE_PATH)
    {{function_name}} = dynamic_import(MODULE, "{{function_name}}")
    {% for class in classes %}
    {{class}} = dynamic_import(MODULE, "{{class}}")
    {% endfor %}
{% else %}
{% endif %}

@dataclass
class {{class_name}}(DTO):
    {% for field in fields %}
    {{ field.name }}: {{ field.type }}
    {% endfor %}

    {% if sync %}    def _query(self, **kwargs){% else %}    async def _query(self, **kwargs){% endif %}:
        return {% if sync %}{% else %}await {% endif %}{{function_name}}(**kwargs)

    {% if sync %}    def run(self, executor: Client, transaction: bool = False){% else %}    async def run(self, executor: AsyncIOClient, transaction: bool = False){% endif %} -> {{return_type}}:
        return {% if sync %}self._run(executor,transaction){% else %}await self._run_async(executor, transaction){% endif %}
""",
    trim_blocks=True,
    lstrip_blocks=True,
)
