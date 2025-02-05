from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.core.views import ZenFilterViewSet, ZenViewSet

router = DefaultRouter()
router.register(
    'zen', ZenFilterViewSet,
    basename='zens'
)
urlpatterns = router.urls
urlpatterns.append(
    path('collection/<str:collection>/zen/<str:name>/version/<str:version>/', ZenViewSet.as_view())
)
