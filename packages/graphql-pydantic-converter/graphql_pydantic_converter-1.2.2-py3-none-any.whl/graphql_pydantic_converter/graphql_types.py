from __future__ import annotations

import json
import typing
from enum import Enum
from string import Template
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

if TYPE_CHECKING:
    from typing import Any
    from typing import Union


class QueryForm(typing.NamedTuple):
    query: str
    variable: typing.Optional[dict[str, Any]] = None


class ENUM(str, Enum):
    ...


class GraphQLType(ENUM):
    STRING = 'String'
    INT = 'Int'
    BOOLEAN = 'Boolean'
    FLOAT = 'Float'
    ID = 'ID'


class Subscription(BaseModel):
    ...

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True
    )


class Interface(BaseModel):
    ...

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True
    )


class GraphqlSchemaType(BaseModel):

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True
    )

    @staticmethod
    def _parse_enum(value: Enum) -> str:
        return f'{value.name}'

    @staticmethod
    def _parse_bool(value: bool) -> str:
        return f'{str(value).lower()}'

    @staticmethod
    def _parse_num(value: int | float) -> str:
        return f'{value}'

    @staticmethod
    def _parse_str(value: Any) -> str:
        try:
            return json.dumps(json.loads(json.dumps(value)))
        except ValueError:
            return f'"{value}"'

    @staticmethod
    def _parse_tuple(value: tuple[Any, ...]) -> str:
        return f'{", ".join(map(str, value))}'


class Payload(BaseModel):

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True
    )

    typename: bool = Field(default=False, alias='__typename')

    def dict_to_custom_string(self, any_object: Any) -> str:
        pairs = []
        match any_object:
            case list():
                for item in any_object:
                    pairs.append(self.dict_to_custom_string(item))
            case dict():
                for key, value in any_object.items():
                    match value:
                        case Payload():
                            pairs.append(f'{key} {{ {value.render()} }}')
                        case dict():
                            pairs.append(f'{key} {{ {self.dict_to_custom_string(value)} }}')
                        case list():
                            for item in any_object:
                                pairs.append(self.dict_to_custom_string(item))
                        case _:
                            if value is True:
                                pairs.append(f'{key}')
        return ' '.join(pairs)

    def render(self) -> str:
        return self.dict_to_custom_string(self.model_dump(exclude_none=True, by_alias=True))


class Input(GraphqlSchemaType):

    def parse_inputs(self, value: Any) -> str:
        match value:
            case Enum():
                response = f'{self._parse_enum(value)}'
            case bool():
                response = f'{self._parse_bool(value)}'
            case int() | float():
                response = f'{self._parse_num(value)}'
            case tuple():
                response = f'{self._parse_tuple(value)}'
            case list():
                values = []
                for item in value:
                    values.append(self.parse_inputs(item))
                response = f'[{", ".join(values)}]'
            case dict():
                pairs = []
                for key, values in value.items():
                    pairs.append(f'{key}: {self.parse_inputs(values)}')
                response = ', '.join(pairs)
            case _:
                response = f'{self._parse_str(value)}'
        return response

    def dict_to_custom_string(self, any_object: Any) -> str:
        pairs = []
        for key, value in any_object.items():
            match value:
                case list():
                    values = []
                    for item in value:
                        values.append(self.parse_inputs(item))
                    pairs.append(f'{key}: [{", ".join(values)}]')
                case dict():
                    values = []
                    for key_nested, value_nested in value.items():
                        values.append(f'{key_nested}: {{{self.parse_inputs(value_nested)}}}')
                    pairs.append(f'{key}: {{{", ".join(values)}}}]')
                case _:
                    pairs.append(f'{key}: {self.parse_inputs(value)}')
        return ', '.join(pairs)

    def render(self) -> str:
        return self.dict_to_custom_string(self.model_dump(exclude_none=True, by_alias=True))


class Mutation(GraphqlSchemaType):
    payload: Payload | bool
    _name: str
    _operation: str = 'mutation'
    _query = Template('$operation $operation_name$variable_def { $projects$aggregations $payload }')

    def dict_to_custom_string(self, value: Any) -> str:
        match value:
            case Input():
                response = f'{{ {value.render()} }}'
            case Enum():
                response = f'{self._parse_enum(value)}'
            case bool():
                response = f'{self._parse_bool(value)}'
            case int() | float():
                response = f'{self._parse_num(value)}'
            case tuple():
                response = f'{self._parse_tuple(value)}'
            case str():
                response = f'{self._parse_str(value)}'
            case list():
                pairs = []
                for item in value:
                    pairs.append(self.dict_to_custom_string(item))
                response = f"[ {', '.join(pairs)}]"
            case dict():
                pairs = []
                for key, values in value.items():
                    pairs.append(f'{key}: {self.dict_to_custom_string(values)}')
                response = f'{{ {", ".join(pairs)} }}'
            case _:
                response = f'{value}'
        return response

    def _inline_variables(self, payload: str) -> QueryForm:
        variables: list[str] = []

        inputs = self.model_dump(exclude={'_name', 'payload'}, exclude_none=True, by_alias=True)
        for name, value in inputs.items():
            variables.append(f' {name}: {self.dict_to_custom_string(value)}')

        arguments = ', '.join(variables)

        return QueryForm(f'mutation {{ {self._name} ({arguments}) {payload} }}')

    def _extracted_variables(self, payload: str) -> QueryForm:
        input_dict: dict[str, Any] = self.model_dump(exclude={'_name', 'payload'}, exclude_none=True, by_alias=True)
        input_vars: dict[str, Any] = json.loads(
            self.model_dump_json(exclude={'_name', 'payload'}, exclude_none=True, by_alias=True)
        )

        model = self.model_fields
        variable_def, arguments_def = '', ''
        variables, arguments = [], []

        for key, value in model.items():
            if key == 'payload':
                continue
            if input_dict.get(value.alias or key) is None:
                continue
            if value.json_schema_extra:
                extra_inputs: dict[str, str] = dict(**value.json_schema_extra)
                input_type = extra_inputs.get('type')
                input_name: str = value.alias if value.alias else key
                variables.append(f'${input_name}: {input_type}')
                arguments.append(f'{value.alias if value.alias else key}: ${input_name}')

        if variables:
            variable_def = f'({", ".join(variables)})'

        if arguments:
            arguments_def = f'({", ".join(arguments)})'

        return QueryForm(
            self._query.substitute(
                operation=self._operation,
                operation_name=self._name,
                variable_def=variable_def,
                projects=self._name,
                aggregations=arguments_def,
                payload=payload
            ),
            input_vars
        )

    def render(self, form: typing.Literal['inline', 'extracted'] = 'extracted') -> QueryForm:
        payload: str = ''
        if isinstance(self.payload, Payload):
            payload = f'{{ {self.payload.render()} }}'
        if form == 'inline':
            return self._inline_variables(payload)
        else:
            return self._extracted_variables(payload)


class Query(GraphqlSchemaType):
    payload: Payload | bool
    _name: str
    _operation: str = 'query'
    _query = Template('$operation $operation_name$variable_def { $projects$aggregations $payload }')

    def parse_inputs(self, value: Any) -> str:
        match value:
            case Enum():
                response = f'{self._parse_enum(value)}'
            case bool():
                response = f'{self._parse_bool(value)}'
            case int() | float():
                response = f'{self._parse_num(value)}'
            case tuple():
                response = f'{self._parse_tuple(value)}'
            case list():
                values = []
                for item in value:
                    values.append(self.parse_inputs(item))
                response = f'[ {",".join(values)} ]'
            case dict():
                pairs = []
                for key, values in value.items():
                    pairs.append(f' {{ {key}: {self.parse_inputs(values)} }} ')
                response = ', '.join(pairs)
            case _:
                response = f'{self._parse_str(value)}'
        return response

    def dict_to_custom_input(self, any_object: Any) -> str:
        pairs = []
        for key, value in any_object.items():
            match value:
                case list():
                    values = []
                    for item in value:
                        values.append(self.parse_inputs(item))
                    pairs.append(f' {key}: [ {", ".join(values)} ] ')
                case dict():
                    values = []
                    for key_nested, value_nested in value.items():
                        values.append(f'{key_nested}: {self.parse_inputs(value_nested)} ')
                    pairs.append(f'{key}: {{ {", ".join(values)} }}')
                case _:
                    pairs.append(f'{key}: {self.parse_inputs(value)}')
        return ', '.join(pairs)

    def dict_to_custom_string(self, any_object: Any) -> str:
        pairs: list[str] = []
        match any_object:
            case list():
                for item in any_object:
                    pairs.append(self.dict_to_custom_string(item))
            case dict():
                for key, value in any_object.items():
                    match value:
                        case Payload():
                            pairs.append(f'{key} {{ {value.render()} }}')
                        case dict():
                            pairs.append(f'{key} {{ {self.dict_to_custom_string(value)} }}')
                        case list():
                            for item in any_object:
                                pairs.append(self.dict_to_custom_string(item))
                        case _:
                            if value is True:
                                pairs.append(f'{key}')
        return ' '.join(pairs)

    def _inline_variables(self,  payload: str) -> QueryForm:
        arguments: str = self.dict_to_custom_input(
            self.model_dump(exclude_none=True, exclude={'_name', 'payload'}, by_alias=True)
        )
        if arguments:
            arguments = f' ( {arguments} )'

        return QueryForm(f'{{ {self._name}{arguments} {payload} }}')

    def _extracted_variables(self, payload: str) -> QueryForm:
        input_dict: dict[str, Any] = self.model_dump(exclude={'_name', 'payload'}, exclude_none=True, by_alias=True)
        input_vars: dict[str, Any] = json.loads(
            self.model_dump_json(exclude={'_name', 'payload'}, exclude_none=True, by_alias=True)
        )

        model = self.model_fields
        variable_def, arguments_def = '', ''
        variables, arguments = [], []

        for key, value in model.items():
            if key == 'payload':
                continue
            if input_dict.get(value.alias or key) is None:
                continue
            if value.json_schema_extra:
                extra_inputs: dict[str, str] = dict(**value.json_schema_extra)
                input_type = extra_inputs.get('type')
                input_name: str = value.alias if value.alias else key
                variables.append(f'${input_name}: {input_type}')
                arguments.append(f'{value.alias if value.alias else key}: ${input_name}')

        if variables:
            variable_def = f'({", ".join(variables)})'

        if arguments:
            arguments_def = f'({", ".join(arguments)})'

        return QueryForm(
            self._query.substitute(
                operation=self._operation,
                operation_name=self._name,
                variable_def=variable_def,
                projects=self._name,
                aggregations=arguments_def,
                payload=payload
            ),
            input_vars
        )

    def render(self, form: typing.Literal['inline', 'extracted'] = 'extracted') -> QueryForm:

        payload: str = ''
        if isinstance(self.payload, Payload):
            payload = f'{{ {self.dict_to_custom_string(self.payload.model_dump(exclude_none=True, by_alias=True))} }}'

        if form == 'inline':
            return self._inline_variables(payload)
        else:
            return self._extracted_variables(payload)


def render(
        queries: Union[Query, Mutation] | typing.Sequence[Union[Query, Mutation]],
        form: typing.Literal['inline', 'extracted']
) -> list[Any]:
    if isinstance(queries, Query | Mutation):
        return list(queries.render(form=form))
    elif isinstance(queries, typing.Sequence):
        list_query: list[QueryForm] = []
        for query in queries:
            list_query.append(query.render(form=form))
        return list_query


def concatenate_queries(queries: typing.Sequence[Union[Query, Mutation]]) -> str:
    merged_query = ''.join(str(query.render(form='inline').query)[1:-1] for query in queries)
    return f'{{ {merged_query} }}'
