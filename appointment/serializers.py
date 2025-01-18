from rest_framework import serializers

from appointment.models import Appointment


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
