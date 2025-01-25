from django.shortcuts import get_object_or_404

from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from core.models import QueryLambda


class QueryLambdasViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    class ParametrizedSerializer(serializers.Serializer):
        class ParameterSerializer(serializers.Serializer):
            name = serializers.CharField()
            value = serializers.JSONField()

        parameters = ParameterSerializer(many=True, read_only=False)

    class QuerySerializer(serializers.ModelSerializer):
        class Meta:
            model = QueryLambda
            fields = '__all__'
            validators = [
                UniqueTogetherValidator(
                    QueryLambda.objects.all(),
                    fields=('name', 'version'),
                    message="This pair name/version is already in use."
                )
            ]

    def get_serializer_class(self):
        if self.action == 'version':
            return self.ParametrizedSerializer
        return self.QuerySerializer

    serializer_class = QuerySerializer
    queryset = QueryLambda.objects.all().order_by('-created_at')

    @action(
        methods=['POST'],
        detail=True, url_path='version/(?P<version>[^/.]+)',
        serializer_class=ParametrizedSerializer
    )
    def version(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        version = kwargs.get('version')
        if version != 'auto':
            lambda_query = get_object_or_404(QueryLambda, name=pk, version=kwargs.get('version'))
        else:
            lambda_query = self.get_queryset().filter(name=pk).first()

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
