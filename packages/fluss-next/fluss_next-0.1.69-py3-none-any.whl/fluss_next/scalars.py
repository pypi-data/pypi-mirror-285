from typing import List, Union, Any, Tuple
from graphql import (
    DocumentNode,
    parse,
    OperationDefinitionNode,
    OperationType,
    print_ast,
    print_source_location,
    print_location,
    GraphQLError,
)
from graphql.language.print_location import print_prefixed_lines


class NodeException(str):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Exception):
            v = str(v)

        if not isinstance(v, str):
            raise TypeError(f"Could not parse Exception {v} as a string")
        # you could also return a string here which would mean model.post_code
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return cls(v)

    def __repr__(self):
        return f"Exception({str(self)})"


EventValue = Union[Tuple[Any, ...], NodeException]


class ValidatorFunction(str):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("ValidatorFunction must be a string")

        return v

    def __repr__(self):
        return f"ValidatorFunction({repr(self)})"


def parse_or_raise(v: str):
    try:
        return parse(v)
    except GraphQLError as e:
        x = repr(e)
        x += "\n" + v + "\n"
        for line in e.locations:
            x += "\n" + print_source_location(e.source, line)
        raise ValueError("Could not parse to graphql: \n" + x)


class SearchQuery(str):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str) and not isinstance(v, DocumentNode):
            raise TypeError(
                "Search query must be either a str or a graphql DocumentNode"
            )
        if isinstance(v, str):
            v = parse_or_raise(v)

        if not v.definitions or len(v.definitions) > 1:
            raise ValueError("Only one definintion allowed")

        if not isinstance(v.definitions[0], OperationDefinitionNode):
            raise ValueError("Needs an operation")

        definition = v.definitions[0]
        if not definition:
            raise ValueError("Specify an operation")

        if not definition.operation == OperationType.QUERY:
            raise ValueError("Needs to be operation")

        assert len(definition.variable_definitions) >= 2, (
            "At least two arguments should be provided ($search: String, $values:"
            f" [ID])): Was given: {print_ast(v)}"
        )

        if (
            definition.variable_definitions[0].variable.name.value != "search"
            or definition.variable_definitions[0].type.kind != "named_type"
        ):
            raise ValueError(
                "First parameter of search function should be '$search: String' if you"
                " provide arguments for your options. This parameter will be filled"
                f" with userinput: Was given: {print_ast(v)}"
            )

        if (
            definition.variable_definitions[1].variable.name.value != "values"
            or definition.variable_definitions[0].type.kind != "named_type"
        ):
            raise ValueError(
                "Seconrd parameter of search function should be '$values: [ID]' if you"
                " provide arguments for your options. This parameter will be filled"
                f" with the default values: Was given: {print_ast(v)}"
            )

        wrapped_query = definition.selection_set.selections[0]

        options_value = (
            wrapped_query.alias.value
            if wrapped_query.alias
            else wrapped_query.name.value
        )
        if options_value != "options":
            raise ValueError(
                "First element of query should be 'options':  Was given:"
                f" {print_ast(v)}"
            )

        wrapped_selection = wrapped_query.selection_set.selections
        aliases = [
            field.alias.value if field.alias else field.name.value
            for field in wrapped_selection
        ]
        if "value" not in aliases:
            raise ValueError(
                "Searched query needs to contain a 'value' not that corresponds to the"
                " selected value"
            )
        if "label" not in aliases:
            raise ValueError(
                "Searched query needs to contain a 'label' that corresponds to the"
                " displayed value to the user"
            )

        return print_ast(v)

    def __repr__(self):
        return f"SearchQuery({repr(self)})"
