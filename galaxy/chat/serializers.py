from rest_framework import serializers
from .models import *

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['username','email']

class GrpUserSerializer(serializers.ModelSerializer):
    
    group_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = GrpUser
        fields = ['group_name', 'user_name', 'group', 'user']

    def get_group_name(self, obj):
        return obj.group.name  # Assuming 'name' is a field in your Group model

    def get_user_name(self, obj):
        return obj.user.username  # Assuming 'username' is a field in your User mo
    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']