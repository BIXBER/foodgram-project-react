from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Cart, Favorite, Follow, Ingredient,
                            IngredientRecipe, Recipe, Tag)
from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import RetrieveListViewSet
from .permissions import AuthorOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserSerializer)
from .utils import build_file
from .pagination import UserPagination, RecipePagination

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer
    pagination_class = UserPagination

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(User, pk=id)
        data = {'user': user.id, 'following': following.id}
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=data, context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, user=user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscribeSerializer(
                self.paginate_queryset(
                    Follow.objects.filter(user=request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter, DjangoFilterBackend)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def create_object(serializers, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'user': user.id, 'recipe': recipe.id}
        serializer = serializers(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(request, pk, model):
        recipe_obj = get_object_or_404(Recipe, id=pk)
        get_object_or_404(model, user=request.user, recipe=recipe_obj).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST',), detail=True)
    def favorite(self, request, pk):
        return self.create_object(FavoriteSerializer, request.user, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_object(request=request, pk=pk, model=Favorite)

    @action(methods=('POST',), detail=True)
    def shopping_cart(self, request, pk):
        return self.create_object(CartSerializer, request.user, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_object(request=request, pk=pk, model=Cart)

    @action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=user).values(
            ingredients=F('ingredient__name'),
            measure=F('ingredient__measurement_unit')).order_by(
            'ingredient').annotate(sum_amount=Sum('amount'))
        return build_file(user, ingredients)
