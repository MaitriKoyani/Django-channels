# from django.db import models

# # Create your models here.

# class User(models.Model):
#     username = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)
#     email = models.EmailField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.username

# class Group(models.Model):
#     name = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

# class GrpUser(models.Model):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     joined_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('group', 'user')

#     def __str__(self):
#         return f"{self.user.username} in {self.group.name}"

# class MessageContent(models.Model):
#     content = models.TextField()

#     def __str__(self):
#         return self.content[:50]  # Display first 50 characters

# class ChatMessage(models.Model):
#     grp_user = models.ForeignKey(GrpUser, on_delete=models.CASCADE)
#     message_content = models.ForeignKey(MessageContent, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.grp_user.user.username} in {self.grp_user.group.name}"
