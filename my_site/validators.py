from django.core.exceptions import ValidationError
import types


def validate_number(value):
    if not isinstance(value, types.IntType):
        msg = 'You have use number'
        return ValidationError(msg)