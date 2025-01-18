from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .social import kakao_get_user, naver_get_user,  google_get_user
from .models import AuthToken, User


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
