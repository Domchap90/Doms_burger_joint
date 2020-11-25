from django.test import TestCase, Client
from .views import is_postcode_valid


class TestHomeView(TestCase):

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')

    def test_is_postcode_valid(self):
        # User enters nothing
        result = is_postcode_valid('')
        self.assertFalse(result)

        # User enters invalid UK postcode
        result = is_postcode_valid('W1 E63')
        self.assertFalse(result)

        # User enters valid UK postcode but not in range of store
        result = is_postcode_valid('MK40 4FE')
        self.assertFalse(result)

        # User enters valid UK postcode in range of store
        result = is_postcode_valid('W1W 7JE')
        self.assertTrue(result)

    def test_check_postcode_home(self):
        url = '/check_postcode_home/'
        fail_msg = "Sorry it looks like you are not eligible for delivery. However \
please feel free to make an order for collection."
        response = self.client.post(url, {'postcode': '00000'})

        # Check session variables are created
        self.assertEqual(len(self.client.session['delivery_eligibility']), 2)

        # Check posting form redirects back to home page
        self.assertRedirects(response, '/')

        self.assertEqual(
            self.client.session['delivery_eligibility']['message'], fail_msg)

        self.client2 = Client()
        self.client2.post(url, {'postcode': 'W1W 7JE'})
        # Delivers success message in event postcode is eligible for delivery
        self.assertEqual(
            self.client2.session['delivery_eligibility']['message'],
            "Good news! You are eligible for delivery.")

        self.client3 = Client()
        self.client3.post(url, {'postcode': 'SW1W 8UT'})
        # Check fail message is delivered when postcode is valid but out of
        # range
        self.assertEqual(
            self.client3.session['delivery_eligibility']['message'], fail_msg)

