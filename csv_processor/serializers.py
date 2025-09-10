# csv_processor/serializers.py
from rest_framework import serializers

class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class TrainMLRequestSerializer(serializers.Serializer):
    features = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    target = serializers.CharField()
    model_type = serializers.ChoiceField(choices=['classification', 'regression'])
    model_name = serializers.CharField()
    algorithm_type = serializers.ChoiceField(
        choices=['random_forest', 'decision_tree', 'logistic', 'linear'],
        default='random_forest'
    )

class TestModelRequestSerializer(serializers.Serializer):
    
    inputs = serializers.DictField(child=serializers.FloatField(), allow_empty=False)

# Nouveau sérialiseur pour DeleteCSVAPIView
class DeleteCSVSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    detail = serializers.CharField(read_only=True)
    
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Feedback

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']



