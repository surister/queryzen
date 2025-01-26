from django.shortcuts import get_object_or_404

from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LambdaQuery


class QueryLambdasViewSet(viewsets.ModelViewSet):
    class ParametrizedSerializer(serializers.Serializer):
        class ParameterSerializer(serializers.Serializer):
            name = serializers.CharField()
            value = serializers.JSONField()

        parameters = ParameterSerializer(many=True, allow_null=True)

    class LambdaQuerySerializer(serializers.ModelSerializer):
        class Meta:
            model = LambdaQuery
            fields = '__all__'

    def get_serializer_class(self):
        if self.action == 'version':
            return self.ParametrizedSerializer
        return self.LambdaQuerySerializer

    serializer_class = LambdaQuerySerializer
    queryset = LambdaQuery.objects.all()

    # lambdas/{lambda_query}
    def retrieve(self, request, pk):
        # TODO: This is what we get, {
        #     "detail": "No LambdaQuery matches the given query."
        # }
        # Change to a more friendly error.
        obj = get_object_or_404(LambdaQuery, name=pk)
        serializer = self.LambdaQuerySerializer(obj)
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=True,
        url_path='version/(?P<version>[^/.]+)',
    )
    def version(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lambda_query = get_object_or_404(LambdaQuery, name=pk, version=kwargs.get('version'))

        result_query = lambda_query.query
        for param in serializer.validated_data['parameters']:
            result_query = result_query.replace(f':{param['name']}', str(param['value']))

        serialized_response = self.LambdaQuerySerializer(
            {
                'name': lambda_query.name,
                'query': result_query,
                'version': lambda_query.version
            }
        )

        return Response(data=serialized_response.data)
