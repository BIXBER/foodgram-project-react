from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    Follow,
    Cart,
    Favorite,
    IngredientRecipe,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )

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
    readonly_fields = ['measurement_unit']
    fields = ['ingredient', 'amount', 'measurement_unit']
    autocomplete_fields = ['ingredient']
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты для рецепта'

    def measurement_unit(self, instance):
        return instance.ingredient.measurement_unit
    measurement_unit.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'text',
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
