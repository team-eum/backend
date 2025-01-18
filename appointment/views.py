from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions, generics
import datetime
import requests

from appointment.models import AppointmentStatus
from appointment.openai import CustomOpenAI
from appointment.serializers import *

from user.models import User
from user.serializers import UserSerializer

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
        
class AdminPageView(APIView):
    permission_classes = [permissions.IsAdminUser]
    # 노인 정보 등록 폼, 노인 및 청년 정보 보내기
    def get(self, request):
        # 데이터 보내기
        junior = User.objects.filter(role="junior").all()
        senior = User.objects.filter(role="senior").all()

        jun_serializer = UserSerializer(junior, many=True).data
        sen_serializer = UserSerializer(senior, many=True).data

        serializer_list = [jun_serializer, sen_serializer]

        content = {
            "status": 1,
            "responseCode": status.HTTP_200_OK,
            "data": serializer_list,
        }
        
        return Response(content)

    def post(self, request):
        # 시니어 등록 폼
        serializer = UserSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("등록 완료", status=status.HTTP_201_CREATED)
        else:
            return Response("등록에 실패했습니다. 고객센터에 문의해주십시오", status=status.HTTP_400_BAD_REQUEST)
        

class AppointmentView(APIView):
    # 매칭된 약속 리스트, 일정 [확인] - 매칭
    def get(self, request, user_id):
        # 약속 리스트
        user = get_object_or_404(request.user)
        if user["role"] == "senior": # 유저가 배우는 사람일 때
            appoinments = Appointment.objects.filter(mentee=user).all()
            
        else: # 유저가 가르쳐주는 사람일 때
            appoinments = Appointment.objects.filter(mentor=user).all()
            
        appoint_list = AppointmentListSerializer(appoinments, many=True).data
        
        return Response(data=appoint_list, status=status.HTTP_200_OK)
    

    def post(self, request, user_id):
        # 자동 매칭
        user = get_object_or_404(id=user_id)
        category = list(user["category"]) # 멘토든 멘티든 카테고리 얻어와야 함
        pre_appoint = {} # 임시 약속 데이터 - {카테고리 : ['멘토', '멘티']}

        if user["role"] == "junior": # user 가 주니어인 경우
            for i in category:
                seniors = User.objects.filter(role="junior").filter(category__contains=i).all() # senior 들 받아오기
                pre_appoint[i] = [user, seniors]

            # 시간 맞추기
            jun_start = datetime.datetime.strptime(i["start"], '%Y-%m-%d %H:%M:%S')
            jun_end = datetime.datetime.strptime(i["end"], '%Y-%m-%d %H:%M:%S')
            
            for i in pre_appoint:
                for j in pre_appoint[i][1]:
                    for k in j.available_date:
                        sen_start = datetime.datetime.strptime(k["start"], '%Y-%m-%d %H:%M:%S')
                        sen_end = datetime.datetime.strptime(k["end"], '%Y-%m-%d %H:%M:%S')
                        if jun_start <= sen_start and sen_end <= jun_end:
                            Appointment.objects.create(mentor=user, 
                                                       mentee=j, 
                                                       start_date=max(jun_start, sen_start) , 
                                                       end_date=min(jun_end, sen_end))
                    

        else: # user 가 시니어인 경우
            for i in category: # 배우고 싶은 필드에 맞는 멘토 필터링
                juniors = User.objects.filter(role="senior").filter(category__contains=i).all()
                pre_appoint[i] = [juniors, user]
            
            # 시간 맞추기


        # 리스트 형식으로 최종 약속 출력
        return Response("매칭 완료", status=status.HTTP_200_OK)

    def put(self, request, jun_id, sen_id, appoinment_id):
        # 약속 [확인]
        junior = get_object_or_404(User, id=jun_id)
        senior = get_object_or_404(User, id=sen_id)

        start_date = request.data['start_date']
        end_date = request.data['end_date']
         # 프론트에서 보내주는 정보명에 따라 달라짐
        appointment = get_object_or_404(Appointment, id=appoinment_id)
        appointment.objects.update(status="ACCEPTED")

        mentor = get_object_or_404(User, id=jun_id)
        mentor.credit += 1

        serializer = AppointmentDetailSerializer(appointment).data
        
        return Response(data=serializer, status=status.HTTP_200_OK)
        


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
