from django import forms
from .models import MemberProfile


class MemberProfileForm(forms.ModelForm):
    class Meta():
        model = MemberProfile
        exclude = ('member', 'reward_status')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'saved_mobile_number': 'Mobile',
            'saved_email': 'Email Address',
            'saved_address_line1': 'Address Line 1',
            'saved_address_line2': 'Address Line 2',
            'saved_postcode': 'Post Code',
            'saved_delivery_instructions': 'Delivery Instructions'
        }

        placeholders = {
            'saved_mobile_number': 'Mobile',
            'saved_email': 'Email Address',
            'saved_address_line1': 'Address Line 1',
            'saved_address_line2': 'Address Line 2',
            'saved_postcode': 'Post Code',
            'saved_delivery_instructions': 'Delivery Instructions'
        }

        # self.fields['name'].widget.attrs['autofocus'] = True
        for field in self.fields: 
            if self.fields[field].required:
                self.fields[field].label = f'{labels[field]}*'
                placeholder = f'{placeholders[field]} (required)'
            else:
                self.fields[field].label = labels[field]
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'member-form'
