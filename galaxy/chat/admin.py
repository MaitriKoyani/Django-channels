from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Member)
admin.site.register(Group)
admin.site.register(GrpUser)
admin.site.register(MessageContent)
admin.site.register(ChatMessage)
admin.site.register(UserToken)
admin.site.register(Friends)
admin.site.register(Request)
admin.site.register(Profile)