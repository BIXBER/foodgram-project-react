from django.contrib import admin
from django.contrib.auth import get_user_model


class AdminUser(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        """Fix django bug: hash password if create user in admin panel."""
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


User = get_user_model()

admin.site.register(User, AdminUser)
