
from rest_framework import serializers
from .models import User, Organization

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'org_id', 'password',)

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('org_id', 'org_name', 'org_description', 'org_secret_key',)