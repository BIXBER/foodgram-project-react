import re

from django.core.exceptions import ValidationError


def hex_validator(value):
    regex_expr = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    if not regex_expr.match(value):
        raise ValidationError('Неверный формат цвета в HEX')
