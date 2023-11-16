from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import (MAX_USERNAME_LENGTH,
                            MAX_EMAILFIELD_LENGTH,
                            MAX_NAME_LENGTH,
                            MAX_PASSWORD_LENGTH)


class User(AbstractUser):

    unicode_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username').capitalize(),
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        help_text=_('Required. Letters, digits and @/./+/-/_ only.'),
        validators=[unicode_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address').capitalize(),
        max_length=MAX_EMAILFIELD_LENGTH,
        unique=True,
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )
    first_name = models.CharField(
        _('first name').capitalize(),
        max_length=MAX_NAME_LENGTH,
    )
    last_name = models.CharField(
        _('last name').capitalize(),
        max_length=MAX_NAME_LENGTH,
    )
    password = models.CharField(
        _('password').capitalize(),
        max_length=MAX_PASSWORD_LENGTH,
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('id',)

    def __str__(self):
        return self.username
