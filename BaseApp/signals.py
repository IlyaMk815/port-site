from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile


# Automatic creation and saving of a profile during user registration with the formation of a default nickname
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.profile = Profile.objects.create(user=instance, nick_name='DefaultNickName'+str(User.objects.count()),
                                                  profile_pic='profile_pics/default/user.png')
    instance.profile.save()
