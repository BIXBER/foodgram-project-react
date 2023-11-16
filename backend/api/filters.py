from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, FilterSet,
                                           NumberFilter)
from rest_framework import filters

from recipes.models import Recipe


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    author = NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=self.request.user)
            return queryset.exclude(favorites__user=self.request.user)
        return queryset.none()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=self.request.user)
            return queryset.exclude(shopping_cart__user=self.request.user)
        return queryset.none()
