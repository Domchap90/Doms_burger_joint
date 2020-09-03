from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta():
        model = Order
        fields = ('name', 'mobile_number', 'email',
                  'address_line1', 'address_line2', 'postcode',
                  'delivery_instructions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'name': 'Name',
            'mobile_number': 'Mobile',
            'email': 'Email Address',
            'address_line1': 'Address Line 1',
            'address_line2': 'Address Line 2',
            'postcode': 'Postal Code',
            'delivery_instructions': 'Any instructions for your driver'
        }

        self.fields['name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False

