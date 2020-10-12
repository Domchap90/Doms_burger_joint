from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


# Create your models here.
class MemberProfile(models.Model):
    member = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_email = models.EmailField(max_length=254, null=True, blank=True)
    saved_mobile_number = models.CharField(max_length=13, null=True, blank=True)
    saved_postcode = models.CharField(max_length=20, null=True, blank=True)
    saved_address_line1 = models.CharField(max_length=80, null=True, blank=True)
    saved_address_line2 = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return self.member.username


@receiver(post_save, sender=User)
def create_or_update_member_info(sender, instance, created, **kwargs):
    if created:
        MemberProfile.objects.create(member=instance)
    if not instance.is_staff:
        instance.memberprofile.save()
