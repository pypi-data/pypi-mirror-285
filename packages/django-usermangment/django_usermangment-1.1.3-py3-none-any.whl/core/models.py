from django.contrib.auth.models import User
from django.db import models
from django.templatetags.static import static


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField( upload_to='avatars/', null=True, blank=True,)
    display_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return f'{self.user}'

    @property
    def name(self):
        if self.display_name:
            return self.display_name
        else:
            return self.user.username

    @property
    def avatar(self):
        if self.profile_pic:
            return self.profile_pic.url
        else:
            avatar = static('images/avatar.svg')
            return avatar
