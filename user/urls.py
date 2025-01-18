from . import views
from django.urls import path

urlpatterns = [
    path("social/<str:provider>",
         views.SocialAuthentication.as_view()),
]
