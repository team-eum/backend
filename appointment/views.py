from openai import OpenAI
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions, generics
import datetime
import requests

from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer, AudioUploadSerializer

from user.models import User
from user.serializers import UserSerializer

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

        appoint_list = AppointmentSerializer(appoinments, many=True).data
        
        return Response(data=appoint_list, status=status.HTTP_200_OK)
    

    def post(self, request, user_id):
        # 자동 매칭
        # start : 2024-01-11 15:30,
        # end : 2024-01-11 16:30
        user = get_object_or_404(id=user_id)
        category = list(user["category"]) # 멘토든 멘티든 카테고리 얻어와야 함
        pre_appoint = {} # 임시 약속 데이터 - {카테고리 : ['멘토', '멘티']}

        if user["role"] == "junior": # user 가 주니어인 경우
            for i in category:
                seniors = User.objects.filter(role="junior").filter(category__contains=i).all() # senior 들 받아오기
                pre_appoint[i] = [user, seniors]

            # 시간 맞추기
            start_date = i["start"][:11].strftime('%Y-%m-%d')
            end_date = i["end"][:11].strftime('%Y-%m-%d')
            start_time = i[12:].strftime('%H:%M')
            end_time = i[12:].strftime('%H:%M')
            
            for i in request.data:
                for j in seniors:
                    for k in seniors.date:
                        pass
                    

                

        else: # user 가 시니어인 경우
            for i in category: # 배우고 싶은 필드에 맞는 멘토 필터링
                juniors = User.objects.filter(role="senior").filter(category__contains=i).all()
                pre_appoint[i] = [juniors, user]
            
        # 시간 맞추기


        # 리스트 형식으로 최종 약속 출력

        return Response()

    def post(self, request, jun_id, sen_id):
        # 약속 [확인]
        junior = get_object_or_404(User, id=jun_id)
        senior = get_object_or_404(User, id=sen_id)

        start_date = request.data['start_date']
        end_date = request.data['end_date']
         # 프론트에서 보내주는 정보명에 따라 달라짐
        appointment = Appointment.objects.create(mentor=junior, 
                                                 mentee=senior, 
                                                 startdate=start_date, 
                                                 enddate=end_date)
        serializer = AppointmentSerializer(appointment).data
        
        return Response(data=serializer, status=status.HTTP_200_OK)
        