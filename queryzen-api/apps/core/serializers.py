from rest_framework import serializers

from apps.core.models import QueryZen, Execution


class CreateZenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryZen
        fields = ('description', 'query')


class DeleteZenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryZen
        fields = ('version',)


class ExecuteZenSerializer(serializers.Serializer):
    parameters = serializers.JSONField(read_only=False)
    version = serializers.CharField()
    database = serializers.CharField()


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = '__all__'


class QueryZenSerializer(serializers.ModelSerializer):
    executions = ExecutionSerializer(many=True)

    class Meta:
        model = QueryZen
        fields = '__all__'


class CollectionsSerializer(serializers.Serializer):
    collection = serializers.CharField()
    zen_count = serializers.IntegerField(min_value=0)


class ZenExecutionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    columns = serializers.JSONField(read_only=True)
    rows = serializers.JSONField(read_only=True)
    execution_time_ms = serializers.IntegerField()
    error = serializers.CharField(allow_blank=True)
    executed_at = serializers.DateTimeField()
    finished_at = serializers.DateTimeField()
    query = serializers.CharField()
