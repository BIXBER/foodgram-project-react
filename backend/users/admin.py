from django.contrib import admin
from django.contrib.auth import get_user_model


class AdminUser(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'username',
        'email',
    )
    list_editable = (
    )
    list_filter = (
        'first_name',
        'email',
    )

    def save_model(self, request, obj, form, change):
        """Исправление ошибки.

        Хэшировать пароль при создании пользователя через админ-панель.
        """
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


User = get_user_model()

admin.site.register(User, AdminUser)
