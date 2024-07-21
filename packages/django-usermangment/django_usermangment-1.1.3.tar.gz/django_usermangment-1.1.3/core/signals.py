from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from allauth.account.utils import send_email_confirmation
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

@receiver(user_signed_up)
def user_signed_up_callback(request, user, **kwargs):
    send_email_confirmation(request, user)

@receiver(post_save, sender=User)
def user_postsave(sender, instance, created, **kwargs):
    user = instance

    # add profile if user is created
    if created:
        Profile.objects.create(
            user=user,
        )
    # else:
    #     # update allauth emailaddress if exists
    #     try:
    #         email_address = EmailAddress.objects.get_primary(user)
    #         if email_address.email != user.email:
    #             email_address.email = user.email
    #             email_address.verified = False
    #             email_address.save()
    #     except:
    #         # if allauth emailaddress doesn't exist create one
    #         EmailAddress.objects.create(
    #             user=user,
    #             email=user.email,
    #             primary=True,
    #             verified=False
    #         )



@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()