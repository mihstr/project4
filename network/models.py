from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following'
    )

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"On {self.timestamp.strftime('%Y-%m-%d at %H:%M:%S')}, {self.user} posted: '{self.content[:50]}...'" if len(self.content) > 50 else f"On {self.timestamp.strftime('%Y-%m-%d at %H:%M:%S')}, {self.user} posted: '{self.content}'"
    
    def likes_count(self):
        return self.likes.count()
    
    class Meta:
        ordering = ['-timestamp']
