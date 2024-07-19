from mimesis import Field
from typing import Any


def _number_field(field: dict) -> float:
    constraints: dict = field["constraints"]
    field_generator = Field()
    return field_generator(
        "numeric.float_number", start=constraints["minimum"], end=constraints["maximum"]
    )


def get_right_field(field: dict) -> Any:
    right_field = _selector_type_of_field(field)
    return right_field(field)


def _selector_type_of_field(field: dict):
    field_type: str = _get_right_key(field)
    different_field = {
        "integer_constraints": _integer_field,
        "integer": _integer_field_without_constraints,
        "string_constraints": _enum_field,
        "number_constraints": _number_field,
    }
    return different_field[field_type]


def _get_right_key(field: dict) -> str:
    field_type: str = field["type"]
    if "constraints" in field:
        return f"{field_type}_constraints"
    return field_type


def _integer_field(field: dict) -> int:
    constraints: dict = field["constraints"]
    field_generator = Field()
    return field_generator(
        "numeric.integer_number", start=constraints["minimum"], end=constraints["maximum"]
    )


def _enum_field(field: dict) -> str:
    enum_list: list = field["constraints"]["enum"]
    field_generator = Field()
    return field_generator("choice", items=enum_list)


def _integer_field_without_constraints(field: dict) -> int:
    field_generator = Field()
    return field_generator("numeric.integer_number")
