from django import forms
from .models import Order
from home.views import is_postcode_valid
from members_area.forms import check_number_format


class OrderFormDelivery(forms.ModelForm):
    class Meta():
        model = Order

        fields = ('name', 'mobile_number', 'email', 'for_collection',
                  'address_line1', 'address_line2', 'postcode',
                  'delivery_instructions')

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')

        if not is_postcode_valid(postcode):
            self.add_error(
                "postcode",
                "Sorry it looks like you are not eligible for delivery" +
                ". However please feel free to make an order for collection."
                )

        return postcode

    def clean_mobile_number(self):
        return check_number_format(self, 'mobile_number')

    def __init__(self, *args, **kwargs):
        super(OrderFormDelivery, self).__init__(*args, **kwargs)

        labels = {
            'name': 'Name',
            'mobile_number': 'Mobile',
            'email': 'Email Address',
            'address_line1': 'Address Line 1',
            'address_line2': 'Address Line 2',
            'postcode': 'Post Code',
            'delivery_instructions': 'Delivery Instructions'
        }

        placeholders = {
            'name': 'First name will do',
            'mobile_number': 'So we can contact you',
            'email': 'To send your confirmation',
            'address_line1': 'Include flat number if applicable',
            'address_line2': '(optional)',
            'postcode': 'e.g. CT11 8AH',
            'delivery_instructions': 'Any instructions for your driver'
        }
        required_fields = ['name', 'mobile_number', 'email', 'address_line1',
                           'postcode']

        self.fields['name'].widget.attrs['autofocus'] = True

        for field in required_fields:
            self.fields[field].required = True

        for field in self.fields:
            if field != 'for_collection':
                self.fields[field].label = labels[field]
                if self.fields[field].required:
                    self.fields[field].label += '*'
                self.fields[field].widget.attrs[
                    'placeholder'] = f'{placeholders[field]}'
                self.fields[field].widget.attrs['class'] = 'stripe-style-input'


class OrderFormCollection(forms.ModelForm):
    class Meta():
        model = Order

        fields = ('name', 'mobile_number', 'email', 'for_collection')

    def clean_mobile_number(self):
        return check_number_format(self, 'mobile_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = {
            'name': 'Name',
            'mobile_number': 'Mobile',
            'email': 'Email Address',
        }

        placeholders = {
            'name': 'First name will do',
            'mobile_number': 'So we can contact you',
            'email': 'To send your confirmation',
        }

        self.fields['name'].widget.attrs['autofocus'] = True
        # self.fields['for_collection'].default = True

        for field in self.fields:
            if field != 'for_collection':
                self.fields[field].required = True
                self.fields[field].label = f"{labels[field]}*"
                self.fields[field].widget.attrs[
                    'placeholder'] = f'{placeholders[field]}'
                self.fields[field].widget.attrs['class'] = 'stripe-style-input'
