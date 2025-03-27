# pylint: disable=C0114
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.core.views import ZenFilterViewSet, ZenView, StatisticsView

router = DefaultRouter()
router.register(
    'zen', ZenFilterViewSet,
    basename='zens'
)
urlpatterns = router.urls
base_path = 'collection/<str:collection>/zen/<str:name>/version/<str:version>/'
urlpatterns.append(
    path(base_path, ZenView.as_view())
)
urlpatterns.append(
    path(
        f'{base_path}stats/',
        StatisticsView.as_view()
    )
)
