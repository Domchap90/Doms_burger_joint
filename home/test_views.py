from django.test import TestCase
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
        response = self.client.post('/check_postcode_home/', {'postcode': '00000'})
        session = self.client.session

        # Check session variables are created
        self.assertEqual(len(session['delivery_eligibility']), 2)

        # Check posting form redirects back to home page
        self.assertRedirects(response, '/')
