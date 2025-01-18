from openai import OpenAI
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer, AudioUploadSerializer


class AppointmentView(APIView):
    """
    Appointment list를 가져올 때 사용하는 API
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            appointments = Appointment.objects.filter(mentee=request.user)
            serializer = AppointmentSerializer(instance=appointments, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AudioIntoTextView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            client = OpenAI()
            serializer = AudioUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            audio = serializer.validated_data['audio']
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="ko",
                response_format="json"
            )
            if transcript:
                return Response(
                    data={"summary": transcript.text},
                    status=status.HTTP_200_OK
                )
            else:
                raise Exception("GPT 오류 발생")
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )