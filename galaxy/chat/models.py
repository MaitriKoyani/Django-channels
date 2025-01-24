from django.db import models
import uuid
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Create your models here.

class Member(models.Model):
    username = models.CharField(max_length=255,unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    @property
    def is_anonymous(self):
        return False
    @property
    def is_authenticated(self):
        return True
    
    def delete(self, *args, **kwargs):
        member = Member.objects.filter(username=self.username).first()
        for grp_user in member.grpuser_set.all():
                    print(grp_user)
                    if grp_user.group.personal or grp_user.group.grpuser_set.count() == 1:
                        
                        gu = grp_user.group
                        guser = GrpUser.objects.filter(group=gu).all()
                        chat_messages = ChatMessage.objects.filter(grp_user__in=guser).all()
                        for chat_message in chat_messages:
                            print(chat_message.message_content)
                            chat_message.message_content.delete() 

                        chat_messages.delete()
                        grp_user.group.delete()
        super(Member, self).delete(*args, **kwargs)


    def __str__(self):
        return self.username

class Group(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    personal = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class GrpUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')


    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class MessageContent(models.Model):
    content = models.TextField()

    def __str__(self):
        return self.content[:50]  # Display first 50 characters

class ChatMessage(models.Model):
    grp_user = models.ForeignKey(GrpUser, on_delete=models.CASCADE)
    message_content = models.ForeignKey(MessageContent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.grp_user.user.username} in {self.grp_user.group.name}"

class UserToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="chat_user_auth_token")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"


class Friends(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    friend = models.ManyToManyField(Member, related_name='friend')
    
    def __str__(self):
        return f"{self.user.username} friends"

class Request(models.Model):
    receiver = models.ForeignKey(Member, on_delete=models.CASCADE)
    sender = models.ManyToManyField(Member, related_name='sender')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receiver.username} request"

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        
        token = request.COOKIES.get('token')
        
        if not token:
            token = request.headers.get('Authorization')
            if not token:
                return None  
        if token.startswith('Token '):
            token = token[6:]  
        
        try:
            
            mtoken = UserToken.objects.filter(token=token).first()
            if mtoken:
                return (mtoken.user, mtoken)
            else:
                
                return None

        except Exception as e:  
            raise AuthenticationFailed('Invalid or expired token.',e)
 
