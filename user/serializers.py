from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
# - **name (String) # 이름**
# - **age (int) # 나이**
# - **area (String, Enum) # 지역**
# - **phone (String) # 핸드폰 번호**
# - **category (String, Enum) # 직무**
# - **available_time (String) # 가능한 시간**

        fields = [
            "name",
            "age",
            "area",
            "phone",
            "category",
            "available_time",
        ]