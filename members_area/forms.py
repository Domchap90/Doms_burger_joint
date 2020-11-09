from django import forms
from .models import MemberProfile
from home.views import is_postcode_valid

import re


class MemberProfileForm(forms.ModelForm):
    class Meta():
        model = MemberProfile
        exclude = ('member', 'reward_status')

    def clean_saved_postcode(self):
        saved_postcode = self.cleaned_data.get('saved_postcode')

        if saved_postcode and not is_postcode_valid(saved_postcode):
            self.add_error(
                "saved_postcode",
                "Sorry it looks like you are not eligible for delivery" +
                ". However please feel free to make an order for collection."
                )

        return saved_postcode

    def clean_saved_mobile_number(self):
        saved_mobile_number = self.cleaned_data['saved_mobile_number']

        if saved_mobile_number:
            formatted_mobile_number = saved_mobile_number.replace(' ', '')

            # Catch any numbers that contain special chars or anything other than
            # numerical digits and '+'
            if re.match("[0-9+]*[^0-9+]+[0-9+]*", formatted_mobile_number):
                self.add_error(
                        'saved_mobile_number',
                        'This phone number contains non numerical characters and is therefore \
not valid.')
                return formatted_mobile_number

            if '+' not in formatted_mobile_number:
                if len(formatted_mobile_number) > 11:
                    self.add_error(
                        'saved_mobile_number',
                        "This phone number is too long. It can only have a maximum \
of 11 digits without a '+'.")
                elif len(formatted_mobile_number) < 10:
                    self.add_error(
                        'saved_mobile_number',
                        "This phone number is too short. It needs a minimum \
of 10 digits without a '+'.")
            else:
                if len(formatted_mobile_number) > 13:
                    self.add_error(
                        'saved_mobile_number',
                        "This phone number is too long. It can only have a maximum \
of 13 digits with a '+'.")
                elif len(formatted_mobile_number) < 12:
                    self.add_error(
                        'saved_mobile_number',
                        "This phone number is too short. It needs a minimum \
of 12 digits with a '+'.")

            return formatted_mobile_number

        return saved_mobile_number

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
