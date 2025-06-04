from rest_framework.serializers import ModelSerializer

from .models import CrimeData, TwitterData

class CrimeDataSerializer(ModelSerializer):
    class Meta:
        model = CrimeData
        fields = "__all__"

class TwitterDataSerializer(ModelSerializer):
    class Meta:
        model = TwitterData
        fields = "__all__"
