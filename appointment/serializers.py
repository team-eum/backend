from rest_framework import serializers

from appointment.models import Appointment
from user.models import User


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


class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
        ]


class TextSummarySerializer(serializers.ModelSerializer):
    mentor = MentorSerializer()

    class Meta:
        model = Appointment
        fields = [
            "mentor",
            "origin_text",
            "summary"
        ]