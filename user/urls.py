from . import views
from django.urls import path

urlpatterns = [
    path("social/<str:provider>",
         views.SocialAuthentication.as_view()),
    path('signin', views.UserSignInAPIView.as_view()),
    path('signup', views.UserSignUpAPIView.as_view()),
    path('modify', views.UserModifyAPIView.as_view()),
    path('sms-auth', views.SmsAuthAPIView.as_view()),
    path('my-info', views.MyPageView.as_view()),
]
