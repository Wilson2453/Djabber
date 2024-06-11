from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Create your models here.

class User(AbstractUser):
    pass


class Room(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    members = models.ManyToManyField(User, related_name='rooms', blank=True, default=None)

    def __str__(self):
        return f"Room: {self.name} owned by {self.owner}"
    

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} by {self.user} saying {self.content}"

    class Meta:
        ordering = ('date_added',)
