from rest_framework.authentication import BaseAuthentication
from user.models import AuthToken


class TokenAuthentication(BaseAuthentication):

    """
    Requires a Authorization header with either formats: "Bearer <token>" / "Token <token>"
    Using Cookies also works: "token: <token>"
    You can also send the token in the query string (NOT RECOMMENDED): "?token=<token>"
    Token is handled on this order: Authorization header > Cookie > QueryString
    """

    def authenticate(self, request):
        if (auth_header := request.META.get("HTTP_AUTHORIZATION")):
            auth_type, _, token = auth_header.partition(' ')
            if auth_type not in ["Token", "Bearer"]:
                return None
        elif (token := request.COOKIES.get("token")) is None:
            if (token := request.GET.get("token")) is None:
                return None
        if not (token.isalnum() and len(token) == 64):
            return None
        try:
            token_obj = AuthToken.objects.select_related('user').get(id=token)
            return (token_obj.user, token_obj)
        except AuthToken.DoesNotExist:
            return None
