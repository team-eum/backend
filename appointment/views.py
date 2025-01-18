from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User

from appointment.models import Appointment, AppointmentStatus
from appointment.openai import CustomOpenAI
from appointment.serializers import *


class AppointmentListView(APIView):
    """
    Appointment list를 가져올 때 사용하는 API
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            appointment_status: Optional[str] = kwargs.get("status")
            if appointment_status and appointment_status.upper() in AppointmentStatus.choices:
                appointments: QuerySet = Appointment.objects.filter(mentee=request.user, status=appointment_status)
                serializer = AppointmentListSerializer(instance=appointments, many=True)
            else:
                appointments: QuerySet = Appointment.objects.filter(mentee=request.user)
                serializer = AppointmentListSerializer(instance=appointments, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AppointmentDetailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            summarized_appointments: Appointment = Appointment.objects.filter(
                mentee=request.user,
                id=kwargs.get("id")
            ).first()
            serializer = AppointmentDetailSerializer(instance=summarized_appointments)
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


class SummaryView(APIView):
    """
    GET : 요약된 텍스트가 있는 Appointment만 반환하는 API
    POST : 텍스트를 요약해주는 API
    """
    permission_classes = [AllowAny]
    client = CustomOpenAI()

    def post(self, request, *args, **kwargs):
        try:
            appointment: Appointment = Appointment.objects.filter(id=kwargs.get("id")).first()
            if not appointment:
                raise ObjectDoesNotExist("해당 약속은 아직 만들어지지 않았습니다.")

            text: str = request.data.get("text")
            summary: str = self.client.get_summary(text)  # OpenAI 호출

            if summary:
                appointment.save_origin_and_summary(text, summary)
                return Response(
                    data={"summary": summary},
                    status=status.HTTP_200_OK
                )
            else:
                raise Exception("OpenAI Error!")
        except ObjectDoesNotExist as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MentorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        request.user (Mentee)가 진행했던 Appointment의 Mentor 정보(id, name) 리스트를 반환하는 API
        """
        try:
            mentors: User = User.objects.filter(appointment_as_mentor__mentee=request.user).distinct()
            serializer = MentorSerializer(instance=mentors, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MentorMenteeListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        mentor의 user id가 주어진 경우, 멘토와 본인이 진행한 모든 Appointment 리스트를 반환하는 API
        """
        try:
            mentor_id: int = kwargs.get("mentor_id")
            appointments: QuerySet = Appointment.objects.filter(mentee=request.user, mentor_id=mentor_id)
            if not appointments:
                raise ObjectDoesNotExist("해당 약속은 아직 멘토와 본인이 진행하지 않습니다.")
            serializer = AppointmentListSerializer(instance=appointments, many=True)
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
