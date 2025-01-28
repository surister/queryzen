from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.core.views import QueryZenViewSet, CollectionsViewSet, ZenApiView

router = DefaultRouter()

router.register('zen', QueryZenViewSet, basename='query-lambdas')
router.register(
    r'collections/(?P<collection_name>\w+)/zen/(?P<zen_name>\w+)',
    CollectionsViewSet,
    basename='collections'
)
urlpatterns = [
    path(r'collections/<str:collection_name>/zen/<str:zen_name>', ZenApiView.as_view(), name='zen-api'),
]
urlpatterns += router.urls
