from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from recipes.models import Tag, Ingredient, Recipe, Follow
from .serializers import (UserCreateSerializer, UserSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeSerializer, SubscribeSerializer,
                          FollowSerializer,)
from .mixins import RetrieveListViewSet
from .permissions import AuthorOrReadOnly


User = get_user_model()


class UserViewSet(UserViewSet):
    serializer_class = UserCreateSerializer

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
        user = get_object_or_404(User, pk=id)
        following = request.user
        data = {'user': user.id, 'following': following.id}
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Follow,
            user=user,
            following=request.user,
        ).delete()
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
                    Follow.objects.filter(following=request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        return queryset.order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
