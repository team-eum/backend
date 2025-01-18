from django.db import models
from main.models import TimeStampedModel


class AppointmentStatus(models.TextChoices):
    PENDING = "PENDING", "대기중"
    ACCEPTED = "ACCEPTED", "수락됨"
    REJECTED = "REJECTED", "거절됨"
    CANCELED = "CANCELED", "취소됨"
    COMPLETED = "COMPLETED", "완료"


class Appointment(TimeStampedModel):
    mentor = models.ForeignKey("user.User", null=True, on_delete=models.SET_NULL, related_name="appointment_as_mentor")
    mentee = models.ForeignKey("user.User", null=True, on_delete=models.SET_NULL, related_name="appointment_as_mentee")
    start_date = models.DateTimeField(null=False)  # 시작 시간
    end_date = models.DateTimeField(null=False)  # 끝나는 시간
    place = models.CharField(max_length=255)  # 약속 위치
    status = models.CharField(choices=AppointmentStatus.choices, max_length=100)  # 약속 상태
    origin_text = models.TextField(null=True)  # 음석 파일에서 추출한 원본 텍스트 데이터
    summary = models.TextField(null=True)  # 원본 텍스트를 요약한 데이터

    class Meta:
        db_table = "appointment"
