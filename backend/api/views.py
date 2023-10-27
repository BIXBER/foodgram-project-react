from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class UserRetrieveListCreateView(UserViewSet):
    serializer_class = UserCreateSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
