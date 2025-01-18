from django.urls import path

from appointment.views import *

app_name = "appointment"

urlpatterns = [
    path("", AppointmentView.as_view(), name="appointment_list"),
    path("<int:id>", AppointmentDetailView.as_view(), name="appointment_detail"),
    path("summary/<int:id>", SummaryView.as_view(), name="summary"),
    path("mentor", MentorListView.as_view(), name="mentor_list"),
    path("mentor/<int:mentor_id>", MentorMenteeListView.as_view(), name="mentor_mentee_list"),
]