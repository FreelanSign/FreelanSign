from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.user.models.models import Profile, User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a Profile instance for the User when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)
