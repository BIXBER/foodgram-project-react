from django.contrib import admin

from .models import Tag


class TagAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


admin.site.register(Tag, TagAdmin)
