from rest_framework import serializers

from apps.core.models import QueryZen, Execution


class CreateZenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryZen
        fields = ('version', 'description', 'query')


class ExecuteZenSerializer(serializers.Serializer):
    parameters = serializers.JSONField()


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = '__all__'


class QueryZenSerializer(serializers.ModelSerializer):
    executions = ExecutionSerializer(many=True)

    class Meta:
        model = QueryZen
        fields = '__all__'
