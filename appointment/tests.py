from django.test import TestCase
from .models import User
from datetime import date

class UserModelTest(TestCase):
    def setUp(self):
        """테스트 환경을 위한 초기 데이터 생성"""
        self.user_data = {
            "username": "johndoe",
            "name": "John Doe",
            "birth": date(1990, 1, 1),
            "phone": "010-1234-5678",
            "role": "Senior",
            "category": ["키오스크 사용법", "은행 앱 사용법"],
            "available_date": {"2025-01-01 9:00-17:00", "2025-01-11 10:00-16:00"},
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
            role=self.user_data["role"],
            help_categories=self.user_data["category"],
            available_date=self.user_data["available_date"],
            credit=self.user_data["credit"],
        )

        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.name, self.user_data["name"])
        self.assertEqual(user.birth, self.user_data["birth"])
        self.assertEqual(user.phone, self.user_data["phone"])
        self.assertEqual(user.category, self.user_data["category"])
        self.assertEqual(user.role, self.user_data["role"])
        self.assertEqual(user.help_categories, self.user_data["help_categories"])
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
        self.assertEqual(user.help_categories, [])

    def test_available_date_json(self):
        """JSONField에 데이터가 저장되는지 테스트"""
        user = User.objects.create(
            username="datesetter",
            name="Date Setter",
            available_date={"Wednesday": "14:00-18:00"},
        )
        self.assertEqual(user.available_date, {"Wednesday": "14:00-18:00"})

    def test_string_representation(self):
        """User 모델의 __str__ 메서드 테스트"""
        user = User.objects.create(
            username="johndoe",
            name="John Doe",
        )
        self.assertEqual(str(user), "johndoe")
