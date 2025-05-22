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
    min_execution_time_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    max_execution_time_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    mean_execution_time_ms = serializers.FloatField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    mode_execution_time_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True,
    )
    median_execution_time_ms = serializers.IntegerField(
        min_value=0,
        read_only=True,
        allow_null=True
    )
    variance = serializers.FloatField(min_value=0, read_only=True, allow_null=True)
    standard_deviation = serializers.FloatField(min_value=0, read_only=True, allow_null=True)
    range = serializers.FloatField(min_value=0, read_only=True, allow_null=True)

    def to_representation(self, instance):
        if instance is None:
            return {field_name: None for field_name in self.fields}
        return super().to_representation(instance)

    @classmethod
    def from_execution(cls, obj, executions):
        return cls(
            instance={
                'min_execution_time_ms': executions.first().total_time,
                'max_execution_time_ms': executions.last().total_time,
                'mean_execution_time_ms': obj.mean_execution_time_in_ms,
                'mode_execution_time_ms': obj.mode_execution_time_in_ms,
                'median_execution_time_ms': obj.median_execution_time_in_ms,
                'variance': obj.variance,
                'standard_deviation': obj.standard_deviation,
                'range': executions.last().total_time - executions.first()
                .total_time,
            }
        )
