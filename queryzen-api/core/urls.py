from core.views import QueryViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('lambdas', QueryViewSet, basename='queries')

urlpatterns = router.urls
