from django.contrib import admin
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string

from .models import (Cart, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'display_color',
        'slug',
    )

    def display_color(self, obj):
        return render_to_string(
            "admin/color_tags_display.html", context={"color": obj.color}
        )
    display_color.short_description = "Цвет в HEX"
    display_color.admin_order_field = "color"

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientRecipeAdmin(admin.TabularInline):
    model = IngredientRecipe
    extra = 3
    min_num = 1
    readonly_fields = ['measurement_unit']
    fields = ['ingredient', 'amount', 'measurement_unit']
    autocomplete_fields = ['ingredient']
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты для рецепта'

    def measurement_unit(self, instance):
        admin.site.empty_value_display = ('Выберите ингредиент для '
                                          'отображения его единицы измерения')
        return instance.ingredient.measurement_unit
    measurement_unit.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'short_text',
        'author',
        'cooking_time',
        'in_favorite_count_display',
        'in_shopping_cart_count_display',
        'pub_date',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    filter_horizontal = ('tags', 'ingredients')
    inlines = (IngredientRecipeAdmin,)

    def short_text(self, obj):
        return truncatechars(obj.text, 150)
    short_text.short_description = 'Описание'

    def in_favorite_count_display(self, obj):
        return obj.favorites.count()
    in_favorite_count_display.short_description = 'Добавлено в избранное'

    def in_shopping_cart_count_display(self, obj):
        return obj.shopping_cart.count()
    in_shopping_cart_count_display.short_description = 'Добавлено в корзину'


admin.site.empty_value_display = 'Не задано'

admin.site.register(Follow)
admin.site.register(Cart)
admin.site.register(Favorite)
