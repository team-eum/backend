from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .social import kakao_get_user, naver_get_user, google_get_user
from .models import SmsAuthCode
from django.contrib.auth import authenticate
from .models import AuthToken, User
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from .serializers import UserSerializer
from django.http import HttpResponse


class SocialAuthentication(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user = None
        try:
            match provider := kwargs.get("provider"):
                case "kakao":
                    user, created = kakao_get_user(request.data)
                case "naver":
                    user, created = naver_get_user(request.data)
                case "google":
                    user, created = google_get_user(request.data)
                case _:
                    return Response(
                        data={
                            "detail": f"Unknown provider {provider}"},
                        status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response(
                data={
                    "detail": f"Invalid Request: {e}"},
                status=status.HTTP_400_BAD_REQUEST)
        if user:
            auth_token = AuthToken.objects.create(user=user)
            return Response(
                data={
                    "token": auth_token.id,
                    "is_new_user": created,
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_200_OK)
        return Response(
            data={
                "detail": f"Cannot get user information from {provider}"},
            status=status.HTTP_401_UNAUTHORIZED)


class UserSignInAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user = authenticate(
            request,
            username=request.data.get("username"),
            password=request.data.get("password"))
        if user:
            auth_token = AuthToken.objects.create(user=user)
            return Response(
                data={
                    "token": auth_token.id,
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_200_OK)
        return Response(
            data={
                "detail": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED)


class UserSignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            auth_token = AuthToken.objects.create(user=user)
            return Response(
                data={
                    "token": auth_token.id,
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class UserModifyAPIView(APIView):
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=UserSerializer(user).data,
                status=status.HTTP_200_OK)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class SmsAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        code = request.data.get("code")
        if not code:
            SmsAuthCode.objects.filter(phone=phone).delete()
            sms_auth = SmsAuthCode.objects.create(phone=phone)
            sms_auth.send_code()
            return Response(
                data={"detail": "Success"},
                status=status.HTTP_200_OK)
        try:
            sms_auth = SmsAuthCode.objects.get(phone=phone)
        except SmsAuthCode.DoesNotExist:
            return Response(
                data={
                    "detail": "Invalid phone number"},
                status=status.HTTP_400_BAD_REQUEST)
        if sms_auth.validate_code(code):
            return Response(
                data={"detail": "Success"},
                status=status.HTTP_200_OK)
        return Response(
            data={"detail": "Invalid code"},
            status=status.HTTP_400_BAD_REQUEST)


class MyPageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # 이름, 사진, 크레딧, 가능 일정 - 수정 및 매칭

    def get(self, request, user_id):
        # 유저 정보
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)

        context = {
            "profile": serializer.data
        }

        return HttpResponse(content=context, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        # 일정 수정
        # available_date = request.data # string 형태로 받아온다고 가정
        user = get_object_or_404(User, id=user_id)
        if request.user.is_authenticated and user == request.user:
            # 프론트에서 어떻게 보내주는지에 따라 달라질 듯
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse("유저 정보가 정상적으로 변경되었습니다.", status=status.HTTP_200_OK)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


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
