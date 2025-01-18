from rest_framework.test import APIClient, APITestCase
from user.models import User
from datetime import date


class UserTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user: User = User.objects.create(
            name="test",
            birth=date(2000, 1, 1),
            phone="010-0000-0000",
            area="seoul",
            career="testtest",
            category=["test1", "test2"],
            role="junior",
            gender="M",
            available_date={
                "start": "2025-01-01 9:00-17:00",
                "end": "2025-01-11 10:00-16:00"
            },
            credit=10
        )
        self.client.force_authenticate(user=self.user)

    def test_my_info_get(self):
        response = self.client.get("/user/my-info")
        self.assertEqual(response.status_code, 200)

    def test_my_info_available_date_update(self):
        update_data = {
                "available_date": {
                    "start": "2025-01-01 9:00-17:00",
                    "end": "2025-01-11 10:00-16:00"
                }
            }
        response = self.client.put(
            path="/user/my-info",
            data=update_data,
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.available_date, update_data["available_date"])

    def test_admin_get(self):
        response = self.client.get("/user/admin")
        self.assertEqual(response.status_code, 200)

    def test_admin_post(self):
        response = self.client.post(
            path="/user/admin",
            data={
                "name": "test",
                "username": "test",
                "role": "S",
                "password": "123",
                "birth": date(2000, 1, 1),
                "phone": "010-0000-0000",
                "area": "seoul",
                "career": "testtest",
                "category": ["test1", "test2"],
                "gender": "M",
                "available_date": {
                    "start": "2025-01-01 9:00-17:00",
                    "end": "2025-01-11 10:00-16:00"
                },
                "credit": 10
            },
            format="json"
        )
        print(response.data)
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        User.objects.all().delete()
