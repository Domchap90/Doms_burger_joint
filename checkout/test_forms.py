from django.test import TestCase
from .forms import OrderFormDelivery, OrderFormCollection


class TestCheckoutForms(TestCase):
    def setUp(self):
        self.customer_info = {
            'name': 'jack',
            'email': 'jack_daniels@tennessee.com',
            'mobile_number': '07711 123 456',
            # Valid postcode
            'postcode': 'SW1Y 4QU',
            'address_line1': 'Flat 12, Chenies Street Chambers',
            'address_line2': '',
            'delivery_instructions': ''
        }
        self.delivery_form = OrderFormDelivery(self.customer_info)
        self.collection_form = OrderFormCollection(self.customer_info)

    def test_clean_postcode_passes_valid_postcode(self):
        self.assertTrue(self.delivery_form.is_valid())

    def test_clean_postcode_fails_invalid_postcode(self):
        # Invalid postcode
        self.customer_info['postcode'] = 'MK403FE'

        self.assertEqual(
            self.delivery_form.errors['postcode'][0],
            "Sorry it looks like you are not eligible for delivery. However \
please feel free to make an order for collection.")

        self.assertFalse(self.delivery_form.is_valid())

    def test_required_fields_have_correct_label(self):
        # Set up form with empty fields
        empty_required_fields = {
            'name': '',
            'email': '',
            'mobile_number': '',
            'postcode': '',
            'address_line1': '',
            'address_line2': '',
            'delivery_instructions': ''
        }
        empty_delivery_form = OrderFormDelivery(data=empty_required_fields)

        # If form field label ends with '*' then it must be required.
        for field in empty_delivery_form:
            if field.label[-1] == '*':
                self.assertEqual(empty_delivery_form.errors[field.name],
                                 ['This field is required.'])
            else:
                self.assertTrue(field.name not in empty_delivery_form.errors)

        # Same test for collection form
        empty_collect_form = OrderFormCollection(data=empty_required_fields)

        for field in empty_collect_form:
            if field.label[-1] == '*':
                self.assertEqual(empty_collect_form.errors[field.name],
                                 ['This field is required.'])
            else:
                self.assertTrue(field.name not in empty_collect_form.errors)

    def test_mobile_is_correct_length(self):
        checkout_form = OrderFormDelivery(
            data={'mobile_number': '01234 567 8912'}
            )

        self.assertEqual(
            checkout_form.errors["mobile_number"],
            ["This phone number is too long. It can only have a maximum of \
11 digits without a '+'."]
        )

        checkout_form = OrderFormCollection(
            data={'mobile_number': '+447835 1234566'}
            )

        self.assertEqual(
            checkout_form.errors["mobile_number"],
            ["This phone number is too long. It can only have a maximum of \
13 digits with a '+'."]
        )

        checkout_form = OrderFormDelivery(
            data={'mobile_number': '01234 5678'}
            )

        self.assertEqual(
            checkout_form.errors["mobile_number"],
            ["This phone number is too short. It needs a minimum \
of 10 digits without a '+'."]
        )

        checkout_form = OrderFormCollection(
            data={'mobile_number': '+4412345678'}
            )

        self.assertEqual(
            checkout_form.errors["mobile_number"],
            ["This phone number is too short. It needs a minimum \
of 12 digits with a '+'."]
        )

        checkout_form = OrderFormDelivery(
            data={'mobile_number': '+44123457 891234'}
            )

        self.assertEqual(
            checkout_form.errors["mobile_number"],
            ["Ensure this value has at most 15 characters (it has 16)."]
        )

    def test_mobile_number_has_no_special_chars(self):

        checkout_form = OrderFormCollection(
            data={'mobile_number': '07535-412-345'}
            )

        self.assertEqual(
            checkout_form.errors['mobile_number'],
            ["This phone number contains non numerical characters and is therefore \
not valid."]
        )

        # Letter 'O' used instead of number '0'
        checkout_form = OrderFormDelivery(
            data={'mobile_number': 'O7535412345'}
            )

        self.assertEqual(
            checkout_form.errors["mobile_number"],
            ["This phone number contains non numerical characters and is therefore \
not valid."]
        )
