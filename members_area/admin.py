from django.contrib import admin
from .models import MemberProfile


class MemberAdmin(admin.ModelAdmin):

    readonly_fields = ('member', )

    fields = ('member', 'reward_status')

    list_display = ('member', 'reward_status')


admin.site.register(MemberProfile, MemberAdmin)