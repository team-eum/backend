from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Q
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.db import transaction
import datetime

from appointment.models import AppointmentStatus
from appointment.openai import CustomOpenAI
from appointment.serializers import *

from user.models import User
from .openai import CustomOpenAI


class AppointmentView(APIView):
    """
    Appointment list를 가져올 때 사용하는 API
    """
    permission_classes = [AllowAny]
    instance = CustomOpenAI()

    def get(self, request, *args, **kwargs):
        try:
            appointment_status: Optional[str] = kwargs.get("status", None)

            # 멘토, 멘티
            # 내 일정 확인하기 ->
            # 1. 내가 가르쳐야 하는 약속과
            # 2. 상대방이 나를 가르쳐야 하는 약속
            # 둘다 보여주어야 한다.
            # role(senior, junior 상관 X)
            appointments = Appointment.objects.filter(status=appointment_status).filter(
                Q(mentee=request.user) | Q(mentor=request.user)
            ).distinct()

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

    def post(self, request):
        # 자동 매칭
        try:
            user = request.user
            
            place = self.instance.get_appropriate_location(user.area)
            category = list(user.data.get("category"))  # 멘토든 멘티든 카테고리 얻어와야 함
            pre_appoint = {}  # 임시 약속 데이터 - {카테고리 : ['멘토', '멘티']}

            if user.role == "J":  # user 가 주니어인 경우
                for i in category:
                    seniors = User.objects.filter(
                        Q(role="S") & Q(place=place) & Q(category__contains=i)
                    )  # senior 들 받아오기
                    pre_appoint[i] = [user, seniors] # 임시 데이터 저장

                # 시간 맞추기
                jun_start = datetime.datetime.strptime(i["start"], '%Y-%m-%d %H:%M:%S')
                jun_end = datetime.datetime.strptime(i["end"], '%Y-%m-%d %H:%M:%S')

                for i in pre_appoint:
                    for j in pre_appoint[i][1]: # 멘티 목록
                        for k in j.available_date:
                            sen_start = datetime.datetime.strptime(k["start"], '%Y-%m-%d %H:%M:%S')
                            sen_end = datetime.datetime.strptime(k["end"], '%Y-%m-%d %H:%M:%S')
                            if jun_start <= sen_start and sen_end <= jun_end:
                                Appointment.objects.create(mentor=user,
                                                           mentee=j,
                                                           place=place,
                                                           start_date=max(jun_start, sen_start),
                                                           end_date=min(jun_end, sen_end)   )

            else:  # user 가 시니어인 경우
                for i in category:
                    juniors = User.objects.filter(
                        Q(role="J") & Q(place=place) & Q(category__contains=i)
                    )   # junior 들 받아오기
                    pre_appoint[i] = [juniors, user] # 임시 데이터 저장

                # 시간 맞추기
                sen_start = datetime.datetime.strptime(i["start"], '%Y-%m-%d %H:%M:%S')
                sen_end = datetime.datetime.strptime(i["end"], '%Y-%m-%d %H:%M:%S')

                for i in pre_appoint:
                    for j in pre_appoint[i][1]: # 멘티 목록
                        for k in j.available_date:
                            jun_start = datetime.datetime.strptime(k["start"], '%Y-%m-%d %H:%M:%S')
                            jun_end = datetime.datetime.strptime(k["end"], '%Y-%m-%d %H:%M:%S')
                            if sen_start <= jun_start and jun_end <= sen_end:
                                Appointment.objects.create(mentor=j,
                                                           mentee=user,
                                                           place=place,
                                                           start_date=max(jun_start, sen_start),
                                                           end_date=min(jun_end, sen_end))

            # 리스트 형식으로 최종 약속 출력
            return Response("매칭 완료", status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(data={"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    def put(self, request, *args, **kwargs):
        try:
            # 약속 [확인]
            mentor_id = request.data['mentor_id']
            mentee_id = request.data['mentee_id']

            # 프론트에서 보내주는 정보명에 따라 달라짐
            mentor = get_object_or_404(User, id=mentor_id)
            mentee = get_object_or_404(User, id=mentee_id)
            appointment = Appointment.objects.filter(id=kwargs.get("appointment_id"), mentor=mentor,
                                                     mentee=mentee).first()
            if not appointment:
                raise ObjectDoesNotExist("Appointment ID, Mentor ID, Mentee ID에 대한 약속이 없습니다.")

            with transaction.atomic():
                appointment.status = "ACCEPTED"
                appointment.save()

                mentor.credit += 1
                mentor.save()

            serializer = AppointmentDetailSerializer(appointment).data
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response(data={"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SummaryView(APIView):
    """
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
