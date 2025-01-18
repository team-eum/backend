from os import getenv
import json

# Social Auth #
KAKAO_REST_API_KEY = getenv('KAKAO_REST_API_KEY')
NAVER_CLIENT_ID = getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = getenv('NAVER_CLIENT_SECRET')
GOOGLE_CLIENT_ID = getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = getenv('GOOGLE_CLIENT_SECRET')

# AWS #
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')

# AWS S3 #
USE_S3 = bool(getenv('USE_S3', False))
AWS_S3_ACCESS_KEY_ID = getenv('AWS_S3_ACCESS_KEY_ID', AWS_ACCESS_KEY_ID)
AWS_S3_SECRET_ACCESS_KEY = getenv(
    'AWS_S3_SECRET_ACCESS_KEY', AWS_SECRET_ACCESS_KEY)
AWS_STORAGE_BUCKET_NAME = getenv('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_EXPIRE = getenv('AWS_QUERYSTRING_EXPIRE', 3600)
AWS_S3_REGION_NAME = getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
AWS_S3_ENDPOINT_URL = getenv(
    "AWS_S3_ENDPOINT_URL", f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
AWS_S3_SIGNATURE_VERSION = getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = getenv("AWS_S3_CUSTOM_DOMAIN")

# Database #
USE_CUSTOM_DB = bool(getenv("USE_CUSTOM_DB", False))
CUSTOM_DB_ENGINE = getenv(
    "CUSTOM_DB_ENGINE", "django.db.backends.mysql")
CUSTOM_DB_NAME = getenv("CUSTOM_DB_NAME", "django")
CUSTOM_DB_USER = getenv("CUSTOM_DB_USER", "django")
CUSTOM_DB_PASSWORD = getenv("CUSTOM_DB_PASSWORD", "django")
CUSTOM_DB_HOST = getenv("CUSTOM_DB_HOST", "db")
CUSTOM_DB_PORT = getenv("CUSTOM_DB_PORT", "3306")
CUSTOM_DB_OPTIONS = json.loads(
    getenv(
        "CUSTOM_DB_OPTIONS",
        '{"charset":"utf8mb4","ssl":{"ca":"/etc/ssl/certs/ca-certificates.crt"}}'))

# CSRF #
CSRF_TRUSTED_ORIGINS = getenv(
    "CSRF_TRUSTED_ORIGINS", "http://localhost").split(",")

# AI APIs #
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = getenv("CLAUDE_API_KEY")
