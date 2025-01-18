from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from openai.types.chat.chat_completion import ChatCompletion
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from appointment.models import Appointment, AppointmentStatus
from appointment.openai import CustomOpenAI
from appointment.serializers import AppointmentSerializer, TextSummarySerializer


class AppointmentView(APIView):
    """
    Appointment list를 가져올 때 사용하는 API
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            appointment_status: Optional[str] = kwargs.get("status")
            if appointment_status in AppointmentStatus.choices:
                appointments: QuerySet = Appointment.objects.filter(mentee=request.user, status=appointment_status)
                serializer = AppointmentSerializer(instance=appointments, many=True)
            else:
                appointments: QuerySet = Appointment.objects.filter(mentee=request.user)
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


class TextSummaryView(APIView):
    """
    텍스트를 요약해주는 API
    """
    permission_classes = [AllowAny]
    client = CustomOpenAI()

    def get(self, request, *args, **kwargs):
        try:
            summarized_appointments: Appointment = Appointment.objects.get(
                mentee=request.user,
                id=kwargs.get("id"),
                summary__isnull=False
            )
            if not summarized_appointments:
                raise ObjectDoesNotExist("해당 약속은 아직 요약 정보가 생성되지 않았습니다.")
            serializer = TextSummarySerializer(instance=summarized_appointments)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, *args, **kwargs):
        try:
            text: str = request.data.get("text")
            summary: ChatCompletion = self.client.get_summary(text)
            if summary:
                return Response(
                    data={"detail": summary.choices[0].message.content},
                    status=status.HTTP_200_OK
                )
            else:
                raise Exception("OpenAI Error!")
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
