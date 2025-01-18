from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self, **kwargs):
        password = self.validated_data.pop('password', None)
        instance = super().save(**kwargs)

        if password:
            instance.set_password(password)
            instance.save()

        return instance
