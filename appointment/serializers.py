from rest_framework import serializers

from appointment.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "mentor",
            "start_date",
            "end_date",
            "place",
            "status",
        ]
        depth = 1


class TextSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = [
            "mentor",
            "origin_text",
            "summary"
        ]
        depth = 1
