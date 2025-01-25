from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import LambdaQuery


class QueryLambdasViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    class ParametrizedSerializer(serializers.Serializer):
        class ParameterSerializer(serializers.Serializer):
            name = serializers.CharField()
            value = serializers.JSONField()

        parameters = ParameterSerializer(many=True)

    class QuerySerializer(serializers.ModelSerializer):
        class Meta:
            model = LambdaQuery
            fields = '__all__'

    def get_serializer_class(self):
        if self.action == 'version':
            return self.ParametrizedSerializer
        return self.QuerySerializer

    serializer_class = QuerySerializer
    queryset = LambdaQuery.objects.all()

    @action(
        methods=['POST'],
        detail=True, url_path='version/(?P<version>[^/.]+)',
        serializer_class=ParametrizedSerializer
    )
    def version(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lambda_query = get_object_or_404(LambdaQuery, name=pk, version=kwargs.get('version'))

        result_query = lambda_query.query
        for param in serializer.validated_data['parameters']:
            result_query = result_query.replace(f':{param['name']}', str(param['value']))

        serialized_response = self.QuerySerializer(
            {
                'name': lambda_query.name,
                'query': result_query,
                'version': lambda_query.version
            }
        )

        return Response(data=serialized_response.data)
