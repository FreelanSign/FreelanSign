from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Profile, User


@receiver(post_save, sender=User)
def ensure_profile(sender, instance: User, created, **kwargs):
    """
    Create a Profile instance for the User if it does not already exist.
    """
    if created and not hasattr(instance, "profile"):
        Profile.objects.get_or_create(user=instance)
