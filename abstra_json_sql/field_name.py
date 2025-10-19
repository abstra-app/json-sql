from .ast import Expression, FunctionCallExpression, NameExpression, SelectField


def field_name(field: SelectField) -> str:
    """
    Get the field name from a SelectField object.
    """
    if field.alias:
        return field.alias
    else:
        return expression_name(field.expression)


def expression_name(expression: Expression):
    """
    Get the field name from an Expression object.
    """
    if isinstance(expression, NameExpression):
        name_parts = expression.name.split(".")
        last_part = name_parts[-1]
        return last_part
    elif isinstance(expression, FunctionCallExpression):
        return expression.name
    else:
        return "?column?"
