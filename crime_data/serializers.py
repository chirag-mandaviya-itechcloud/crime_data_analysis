from rest_framework.serializers import ModelSerializer

from .models import CrimeData

class CrimeDataSerializer(ModelSerializer):
    class Meta:
        model = CrimeData
        fields = "__all__"
