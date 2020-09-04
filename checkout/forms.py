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

        self.fields['name'].widget.attrs['autofocus'] = True
        for field in self.fields: 
            if self.fields[field].required:
                self.fields[field].label = f'{labels[field]}*'
                placeholder = f'{placeholders[field]} (required)'
            else:
                self.fields[field].label = labels[field]
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            
