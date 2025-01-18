from django.urls import path

from appointment.views import SummaryView, AppointmentListView, MentorListView, MentorMenteeListView

app_name = "appointment"

urlpatterns = [
    path("", AppointmentListView.as_view(), name="appointment_list"),
    path("summary/<int:id>", SummaryView.as_view(), name="summary"),
    path("mentor", MentorListView.as_view(), name="mentor_list"),
    path("mentor/<id:mentor_id>", MentorMenteeListView.as_view(), name="mentor_mentee_list"),
]