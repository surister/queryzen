"""
DRF Serializers for apps.core views.
"""
from rest_framework import serializers

from apps.core.models import Zen, Execution


class CreateZenSerializer(serializers.ModelSerializer):
    default_parameters = serializers.JSONField(read_only=False, required=False)

    class Meta:
        model = Zen
        fields = ('description', 'query', 'default_parameters')


class ExecuteZenSerializer(serializers.Serializer):
    parameters = serializers.JSONField(read_only=False)
    version = serializers.CharField()
    database = serializers.CharField()


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        exclude = ('zen',)


class ZenExecutionResponseSerializer(ExecutionSerializer):
    columns = serializers.JSONField(read_only=True)
    rows = serializers.JSONField(read_only=True)


class ZenSerializer(serializers.ModelSerializer):
    executions = ExecutionSerializer(many=True)

    class Meta:
        model = Zen
        fields = '__all__'


class CollectionsSerializer(serializers.Serializer):
    collection = serializers.CharField()
    zen_count = serializers.IntegerField(min_value=0)


class StatisticsSerializer(serializers.Serializer):
    """Statistics serializer for Zen executions"""
    min_execution_time_in_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    max_execution_time_in_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    mean_execution_time_in_ms = serializers.FloatField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    mode_execution_time_in_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    median_execution_time_in_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    variance = serializers.FloatField(min_value=0, read_only=True)
    standard_deviation = serializers.FloatField(min_value=0, read_only=True)
    range = serializers.FloatField(min_value=0, read_only=True)
