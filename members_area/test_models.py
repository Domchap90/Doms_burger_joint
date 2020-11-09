from django.test import TestCase
from django.contrib.auth.models import User
from .models import MemberProfile


class TestMembersAreaModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jamesDean')
        self.james_profile = MemberProfile(member=self.user)

    def test_defaults(self):
        # Check reward status defaults to 0
        self.assertEqual(self.james_profile.reward_status, 0)

    def test_string_methods(self):
        # Check member object returns string of username
        self.assertEqual(str(self.james_profile), 'jamesDean')

    def test_create_or_update_member_info(self):
        self.user.username = 'sirJamesDean'

        # Check member's username is updated as the username changes
        self.assertEqual(self.james_profile.member.username,
                         self.user.username)
