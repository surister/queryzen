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
