from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)

RECIPE_MAX_PAGE_SIZE = 6
USER_MAX_PAGE_SIZE = 10
USER_PAGINATION_DEFAULT_LIMIT = 10


class RecipePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = RECIPE_MAX_PAGE_SIZE


class UserPagination(PageNumberPagination, LimitOffsetPagination):
    page_size_query_param = 'limit'
    default_limit = USER_PAGINATION_DEFAULT_LIMIT
    page_size = USER_MAX_PAGE_SIZE
