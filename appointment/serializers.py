from rest_framework import serializers

from appointment.models import Appointment
from user.models import User


class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
        ]


class MenteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
        ]


class AppointmentListSerializer(serializers.ModelSerializer):
    mentor = MentorSerializer()
    mentee = MenteeSerializer()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "mentor",
            "mentee",
            "start_date",
            "end_date",
            "place",
            "status"
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    mentor = MentorSerializer()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "mentor",
            "start_date",
            "end_date",
            "place",
            "status",
            "origin_text",
            "summary"
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
