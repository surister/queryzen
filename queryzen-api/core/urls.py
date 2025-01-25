from rest_framework.routers import DefaultRouter

from core.views import QueryLambdasViewSet

router = DefaultRouter()

router.register('lambdas', QueryLambdasViewSet, basename='query-lambdas')

urlpatterns = router.urls
