from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.core.views import TransversalZenViewSet, CollectionsViewSet

router = DefaultRouter()

router.register(
    'zen', TransversalZenViewSet,
    basename='zens'
)
router.register(
    r'collections',
    CollectionsViewSet,
    basename='collections'
)

urlpatterns = router.urls
