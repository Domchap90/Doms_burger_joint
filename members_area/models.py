from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


# Create your models here.
class MemberProfile(models.Model):
    member = models.OneToOneField(User, on_delete=models.CASCADE)
    reward_status = models.IntegerField(default=0, editable=True)
    saved_email = models.EmailField(max_length=254, null=True, blank=True)
    saved_mobile_number = models.CharField(
        max_length=15, null=True, blank=True)
    saved_postcode = models.CharField(max_length=9, null=True, blank=True)
    saved_address_line1 = models.CharField(
        max_length=80, null=True, blank=True)
    saved_address_line2 = models.CharField(max_length=80, null=True,
                                           blank=True)
    saved_delivery_instructions = models.CharField(
        max_length=100, null=True, blank=True)

    def __str__(self):
        return self.member.username


@receiver(post_save, sender=User)
def create_or_update_member_info(sender, instance, created, **kwargs):
    if created:
        MemberProfile.objects.create(member=instance)
    instance.memberprofile.save()
