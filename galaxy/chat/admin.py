from django.contrib import admin

# Register your models here.

from .models import User, Group, GrpUser, MessageContent, ChatMessage

admin.site.register(User)
admin.site.register(Group)
admin.site.register(GrpUser)
admin.site.register(MessageContent)
admin.site.register(ChatMessage)
