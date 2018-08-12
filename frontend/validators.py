from django.core.exceptions import ValidationError


def validate_cellphone(value):
    if not value.startswith('69'):
        raise ValidationError('This is not a correct cellphone number')

def validate_number(value):
    try:
        value=int(value)
    except:
        value=value
    print(value)
    if not isinstance(value, int):
        print('problem')
        msg = 'You have use number'
        raise ValidationError(msg)
    