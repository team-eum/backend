from django.test import TestCase
from user.models import User
from datetime import date
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Appointment, AppointmentStatus
from rest_framework import status

class UserModelTest(TestCase):
    def setUp(self):
        """테스트 환경을 위한 초기 데이터 생성"""
        self.user_data = {
            "username": "johndoe",
            "name": "John Doe",
            "birth": date(1990, 1, 1),
            "phone": "010-1234-5678",
            "category": {"category": ["키오스크 사용법", "은행 앱 사용법"]},
            "available_date": {"start": "2025-01-01 9:00-17:00", "end": "2025-01-11 10:00-16:00"},
            "credit": 10,
        }

    def test_create_user(self):
        """User 모델 생성 테스트"""
        user = User.objects.create(
            username=self.user_data["username"],
            name=self.user_data["name"],
            birth=self.user_data["birth"],
            phone=self.user_data["phone"],
            category=self.user_data["category"],
            available_date=self.user_data["available_date"],
            credit=self.user_data["credit"],
        )
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.name, self.user_data["name"])
        self.assertEqual(user.birth, self.user_data["birth"])
        self.assertEqual(user.phone, self.user_data["phone"])
        self.assertEqual(user.category, self.user_data["category"])
        self.assertEqual(user.role, "J")
        self.assertEqual(user.available_date, self.user_data["available_date"])
        self.assertEqual(user.credit, self.user_data["credit"])

    def test_role_choices(self):
        """ROLE_CHOICES 값 테스트"""
        user = User.objects.create(
            username="adminuser",
            name="Admin User",
            role="Admin",
        )
        user.role = "A"  # Admin 역할로 설정
        user.save()
        self.assertEqual(user.role, "A")

    def test_default_credit(self):
        """기본 credit 값 테스트"""
        user = User.objects.create(
            username="newuser",
            name="New User",
        )
        self.assertEqual(user.credit, 5)

    def test_help_categories_blank(self):
        """help_categories가 빈 리스트로 초기화되는지 테스트"""
        user = User.objects.create(
            username="nocategories",
            name="No Categories User",
        )
        

    def test_available_date_json(self):
        """JSONField에 데이터가 저장되는지 테스트"""
        user = User.objects.create(
            username="datesetter",
            name="Date Setter",
            available_date={"start" : "2025-01-11 14:00", "end": "2025-01-11 18:00"},
        )
        self.assertEqual(user.available_date, {'start': '2025-01-11 14:00', 'end': '2025-01-11 18:00'})

    def test_string_representation(self):
        """User 모델의 __str__ 메서드 테스트"""
        user = User.objects.create(
            username="johndoe",
            name="John Doe",
        )
        self.assertEqual(str(user), "johndoe")


User = get_user_model()

class AppointmentViewTest(APITestCase):
    def setUp(self):
        """테스트를 위한 초기 데이터 설정"""
        # 멘토 (Senior) 생성
        self.senior = User.objects.create_user(
            username="mentor_user",
            password="testpassword",
            role="S",
            category={"category": ["키오스크 사용법"]},
            available_date={"start": "2025-01-01 09:00:00", "end": "2025-01-11 17:00:00"}
        )
        
        # 멘티 (Junior) 생성
        self.junior = User.objects.create_user(
            username="mentee_user",
            password="testpassword",
            role="J",
            category={"category": ["키오스크 사용법", "은행앱 사용법"]},
            available_date={"start": "2025-01-01 10:00:00", "end": "2025-01-10 16:00:00"}
        )
        
        # 클라이언트 설정
        self.client = APIClient()
        self.appointment_url = "/appointment/"

    def test_get_appointments(self):
        """GET 요청 테스트 - 약속 리스트 조회"""
        # 테스트를 위해 Appointment 생성
        appointment = Appointment.objects.create(
            mentor=self.junior,
            mentee=self.senior,
            start_date="2025-01-02 10:00:00",
            end_date="2025-01-02 16:00:00",
            status="PENDING"
        )
        
        # Junior로 로그인
        self.client.force_authenticate(user=self.junior)

        # GET 요청
        response = self.client.get(self.appointment_url)
        
        # 응답 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # self.assertEqual(response.data[0]["mentor"], self.senior.id)
        # self.assertEqual(response.data[0]["mentee"], self.junior.id)

    def test_post_appointments_as_junior(self):
        """POST 요청 테스트 - Junior가 약속 생성 요청"""
        self.client.force_authenticate(user=self.junior)
        
        # POST 요청
        print("post 유저 : ", self.junior)
        response = self.client.post(self.appointment_url)
        print("post 응답 : ", response.data)
        
        # 응답 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.mentor, self.senior)
        self.assertEqual(appointment.mentee, self.junior)
        self.assertEqual(appointment.start_date, "2025-01-01 10:00:00")
        self.assertEqual(appointment.end_date, "2025-01-10 16:00:00")

    def test_post_appointments_as_senior(self):
        """POST 요청 테스트 - Senior가 약속 생성 요청"""
        self.client.force_authenticate(user=self.senior)
        
        # POST 요청
        response = self.client.post(self.appointment_url)
        print(response.data)
        
        # 응답 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.mentor, self.senior)
        self.assertEqual(appointment.mentee, self.junior)
        self.assertEqual(appointment.start_date, "2025-01-01 10:00:00")
        self.assertEqual(appointment.end_date, "2025-01-10 16:00:00")

    # def test_invalid_user_role(self):
    #     """POST 요청 테스트 - 잘못된 role의 사용자"""
    #     # Junior로 로그인
    #     invalid_user = User.objects.create_user(
    #         username="invalid_user",
    #         password="testpassword",
    #         role="A",  # Admin 역할
    #         category={"category": ["키오스크 사용법"]},
    #     )
    #     self.client.force_authenticate(user=invalid_user)
        
    #     # POST 요청
    #     response = self.client.post(self.appointment_url)
        
    #     # 응답 데이터 확인
    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     self.assertIn("detail", response.data)


