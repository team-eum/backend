from django.urls import path

from appointment.views import TextSummaryView, AppointmentView

app_name = "appointment"

urlpatterns = [
    path("", AppointmentView.as_view(), name="appointment_list"),
    path("summary", TextSummaryView.as_view(), name="summary"),
]