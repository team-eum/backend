from rest_framework import serializers

from appointment.models import Appointment


class AudioUploadSerializer(serializers.Serializer):
    audio = serializers.FileField()


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "mentor",
            "start_date",
            "end_date",
            "place",
            "status",
            "origin_text",
            "summary",
        ]
        depth = 1
