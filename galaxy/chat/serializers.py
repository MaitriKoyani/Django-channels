from rest_framework import serializers
from .models import *

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['username','email']

class GrpUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrpUser
        fields = ['group','user']