from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserPerformanceProfile


@receiver(post_save, sender=CustomUser)
def create_performance_profile(sender, instance, created, **kwargs):
    if created:
        UserPerformanceProfile.objects.create(user=instance)