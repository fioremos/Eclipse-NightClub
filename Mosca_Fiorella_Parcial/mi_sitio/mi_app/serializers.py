from rest_framework import serializers
from .models import SolicitudConsulta

class SolicitudConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudConsulta
        fields = '__all__'