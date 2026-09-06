from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Name must contain at least 3 characters."
            )
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError(
                "Email is required."
            )
        return value

    def validate(self, data):
        if data.get('age') is not None and data['age'] <= 0:
            raise serializers.ValidationError(
                "Age must be greater than 0."
            )

        return data