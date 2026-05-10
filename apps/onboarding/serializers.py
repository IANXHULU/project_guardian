from rest_framework import serializers
from .models import OnboardingRequest


class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingRequest
        fields = "__all__"

    def create(self, validated_data):
        return OnboardingRequest.objects.create(**validated_data)