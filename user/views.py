from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .social import kakao_get_user, naver_get_user,  google_get_user
from .models import AuthToken, User
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions, generics
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
                    # "user": UserSignInSerializer(user).data
                },
                status=status.HTTP_200_OK)
        return Response(
            data={
                "detail": f"Cannot get user information from {provider}"},
            status=status.HTTP_401_UNAUTHORIZED)
    
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
            serializer = UserSerializer(user, data=request.data) # 프론트에서 어떻게 보내주는지에 따라 달라질 듯
            if serializer.is_valid():
                serializer.save()
                return HttpResponse("유저 정보가 정상적으로 변경되었습니다.", status=status.HTTP_200_OK)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


