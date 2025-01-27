from django.db import models
import uuid
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import random
uid = random.randint(1000000, 9999999)
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
    
    def save(self, *args, **kwargs):
        super(Member, self).save(*args, **kwargs)
        try:
            Profile.objects.create(user=self)
        except Exception as e:
            print(f"Error while creating profile for member {self.username}: {e}")
        
    
    def delete(self, *args, **kwargs):
        try:
            for grp_user in self.grpuser_set.all():
                print(grp_user)
                
                if grp_user.group.personal or not grp_user.group.grpuser_set.exclude(id=grp_user.id).exists():
                    
                    gu = grp_user.group
                    guser = GrpUser.objects.filter(group=gu)
                    chat_messages = ChatMessage.objects.filter(grp_user__in=guser)
                    
                    for chat_message in chat_messages:
                        print(chat_message.message_content)
                        chat_message.delete()  # Deleting chat message safely
                    
                    chat_messages.delete()
                    gu.delete()
            
            super(Member, self).delete(*args, **kwargs)
        
        except Exception as e:
            print(f"Error while deleting member {self.username}: {e}")



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
    user = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='friends')
    friend = models.ManyToManyField(Member, related_name='friend')
    
    def __str__(self):
        return f"{self.user.username} friends"

class Request(models.Model):
    receiver = models.ForeignKey(Member, on_delete=models.CASCADE,related_name='receiver')
    sender = models.ManyToManyField(Member, related_name='sender')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        return f"{self.receiver.username} request"

def generate_unique_id():

    return str(random.randint(1000000, 9999999))

class Profile(models.Model):
    
    user = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='profile')
    up_id = models.CharField(max_length=255, unique=True,default=generate_unique_id)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    bio = models.CharField(max_length=255,default='Enjoying Chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} profile"

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
 
