from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserRetrieveListCreateView, TagDetailListView

app_name = 'api'

router = DefaultRouter()

router.register(r'^users', UserRetrieveListCreateView)
router.register(r'^tags', TagDetailListView)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
