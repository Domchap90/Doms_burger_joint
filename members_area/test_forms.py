from django.test import TestCase
from .forms import MemberProfileForm


class TestMembersAreaForm(TestCase):

    def test_saved_mobile_number_correct_length(self):
        member_form = MemberProfileForm(
            data={'saved_mobile_number': '01234 567 8912'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["This phone number is too long. It can only have a maximum of \
11 digits without a '+'."]
        )

        member_form = MemberProfileForm(
            data={'saved_mobile_number': '+447835 1234566'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["This phone number is too long. It can only have a maximum of \
13 digits with a '+'."]
        )

        member_form = MemberProfileForm(
            data={'saved_mobile_number': '01234 5678'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["This phone number is too short. It needs a minimum \
of 10 digits without a '+'."]
        )

        member_form = MemberProfileForm(
            data={'saved_mobile_number': '+4412345678'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["This phone number is too short. It needs a minimum \
of 12 digits with a '+'."]
        )

        member_form = MemberProfileForm(
            data={'saved_mobile_number': '+44123457 891234'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["Ensure this value has at most 15 characters (it has 16)."]
        )

    def test_saved_mobile_number_has_no_special_chars(self):

        member_form = MemberProfileForm(
            data={'saved_mobile_number': '07535-412-345'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["This phone number contains non numerical characters and is therefore \
not valid."]
        )

        # Letter 'O' used instead of number '0'
        member_form = MemberProfileForm(
            data={'saved_mobile_number': 'O7535412345'}
            )

        self.assertEqual(
            member_form.errors["saved_mobile_number"],
            ["This phone number contains non numerical characters and is therefore \
not valid."]
        )

    def test_saved_postcode_is_valid(self):
        # User enters invalid UK postcode
        member_form = MemberProfileForm(
            data={"saved_postcode": "W1 E63"}
            )

        self.assertEqual(
            member_form.errors["saved_postcode"],
            ["Sorry it looks like you are not eligible for delivery" +
             ". However please feel free to make an order for collection."]
        )

        # User enters valid UK postcode but not in range of store
        member_form = MemberProfileForm(
            data={"saved_postcode": "MK40 4FE"}
            )

        self.assertEqual(
            member_form.errors["saved_postcode"],
            ["Sorry it looks like you are not eligible for delivery" +
             ". However please feel free to make an order for collection."]
        )

        # User enters valid UK postcode in range of store
        member_form = MemberProfileForm(
            data={"saved_postcode": "W1W 7JE"}
            )

        self.assertTrue(member_form.is_valid())
