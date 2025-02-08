# pylint: disable=C0114
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.core.views import ZenFilterViewSet, ZenView, ZenStatsAPIView

router = DefaultRouter()
router.register(
    'zen', ZenFilterViewSet,
    basename='zens'
)
urlpatterns = router.urls
urlpatterns.extend(
    (path('collection/<str:collection>/zen/<str:name>/version/<str:version>/', ZenView.as_view()),
     path('collection/<str:collection>/zen/<str:name>/version/<str:version>/stats/', ZenStatsAPIView.as_view()))
)
