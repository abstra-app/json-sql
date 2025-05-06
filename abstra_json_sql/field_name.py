from .ast import SelectField, NameExpression


def field_name(field: SelectField) -> str:
    """
    Get the field name from a SelectField object.
    """
    if field.alias:
        return field.alias
    elif isinstance(field.expression, NameExpression):
        return field.expression.name
    else:
        return "?column?"
