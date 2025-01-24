from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from core.models import Query

from rest_framework import mixins, serializers, viewsets, status


class QueryViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    class QuerySerializer(serializers.ModelSerializer):
        class Meta:
            model = Query
            fields = '__all__'

    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def retrieve(self, request, *args, **kwargs):
        query = get_object_or_404(Query, pk=self.kwargs['pk'])
        return Response(self.get_serializer(query).data, status=status.HTTP_200_OK)
