import requests
from django.conf import settings
from .models import SocialConnector, User
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

KAKAO_REST_API_KEY = settings.KAKAO_REST_API_KEY
NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET


def get_or_create_user(social_provider, social_id):
    is_new_user_created = False
    try:
        social_connector = SocialConnector.objects.get(
            social_provider=social_provider,
            social_id=social_id)
        user = social_connector.user
    except SocialConnector.DoesNotExist:
        user = User.objects.create(user_type="U")
        social_connector = SocialConnector.objects.create(
            social_provider=social_provider,
            social_id=social_id,
            user=user)
        is_new_user_created = True
    return user, is_new_user_created


def kakao_get_access_token(data):
    redirect_uri = data.get("redirect_uri")
    code = data.get("code")
    if not redirect_uri or not code:
        raise ValueError("redirect_uri and code is required")
    url = 'https://kauth.kakao.com/oauth/token'
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'}

    body = {'grant_type': 'authorization_code',
            'client_id': KAKAO_REST_API_KEY,
            'redirect_uri': redirect_uri,
            'code': code}
    kakao_token_response = requests.post(url, headers=headers, data=body)
    kakao_token_response = kakao_token_response.json()
    error = kakao_token_response.get("error", None)
    if error:
        return None

    access_token = kakao_token_response.get("access_token")
    return access_token


def kakao_get_user(data):
    access_token = kakao_get_access_token(data)
    if not access_token:
        return None
    url = 'https://kapi.kakao.com/v2/user/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    kakao_response = requests.post(url, headers=headers)
    kakao_response = kakao_response.json()
    return get_or_create_user('kakao', kakao_response['id'])


def naver_get_access_token(data):
    code = data.get('code')
    state = data.get('state')
    redirect_uri = data.get('redirect_uri')
    client_id = NAVER_CLIENT_ID
    client_secret = NAVER_CLIENT_SECRET

    base_url = 'https://nid.naver.com/oauth2.0/token'
    params = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code,
        'state': state
    }
    response = requests.get(base_url, params=params, timeout=30)
    response = response.json()
    error = response.get('error')
    if error:
        return None
    access_token = response.get('access_token')
    return access_token


def naver_get_user(data):
    access_token = naver_get_access_token(data)
    if not access_token:
        return None
    header = "Bearer " + access_token
    url = 'https://openapi.naver.com/v1/nid/me'
    headers = {
        'Authorization': header
    }
    naver_response = requests.get(url, headers=headers, timeout=30)
    response = naver_response.json()
    return get_or_create_user('naver', response['response']['id'])


def google_get_user(data):
    url = 'https://oauth2.googleapis.com/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': data.get('redirect_uri'),
        'code': data.get('code'),
    }
    response = requests.post(url=url, data=data)
    if not response.ok:
        return None
    data = response.json()
    token = data.get('id_token')
    idinfo = id_token.verify_oauth2_token(
        token, google_requests.Request(), GOOGLE_CLIENT_ID)
    return get_or_create_user('google', idinfo['sub'])
