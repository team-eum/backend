from django.conf import settings
import requests
import time
import datetime
import uuid
import hmac
import hashlib

SOLAPI_API_KEY = settings.SOLAPI_API_KEY
SOLAPI_API_SECRET = settings.SOLAPI_API_SECRET
SOLAPI_FROM_NUMBER = settings.SOLAPI_FROM_NUMBER


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def get_signature(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(apiKey, apiSecret):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {'Authorization': 'HMAC-SHA256 ApiKey=' + apiKey + ', Date=' + date + ', salt=' + salt + ', signature=' +
                             get_signature(apiSecret, data)}


def send_sms(to, text):
    data = {
        'message': {
            'to': to,
            'from': SOLAPI_FROM_NUMBER,
            'text': text
        }
    }
    res = requests.post('https://api.solapi.com/messages/v4/' + 'send',
                        headers=get_headers(SOLAPI_API_KEY, SOLAPI_API_SECRET), json=data)
    return res.json()
