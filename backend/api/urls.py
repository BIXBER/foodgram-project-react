from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserView, TagView, IngredientView

app_name = 'api'

router = DefaultRouter()

router.register(r'^users', UserView)
router.register(r'^tags', TagView)
router.register(r'^ingredients', IngredientView)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
