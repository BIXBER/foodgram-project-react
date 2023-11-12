from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class AdminUser(UserAdmin):
    list_display = (
        'first_name',
        'last_name',
        'username',
        'email',
    )
    list_filter = (
        'first_name',
        'email',
    )
    add_fieldsets = (
        (None, {
            'fields': (
                *User.REQUIRED_FIELDS, User.USERNAME_FIELD,
                'password1', 'password2', 'is_superuser', 'is_staff',
            )
        }),
    )


admin.site.empty_value_display = 'Не задано'
