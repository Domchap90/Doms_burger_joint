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
        return check_number_format(self, 'saved_mobile_number')

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
        required = [
            'saved_mobile_number',
            'saved_email',
            'saved_address_line1',
            'saved_postcode']

        self.fields['saved_email'].widget.attrs['autofocus'] = True

        for field in required:
            self.fields[field].required = True

        for field in self.fields:
            if self.fields[field].required:
                self.fields[field].label = f'{labels[field]}*'
                placeholder = f'{placeholders[field]} (required)'
            else:
                self.fields[field].label = labels[field]
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'member-form'


def check_number_format(form_instance, number_key):
    number = form_instance.cleaned_data[number_key]

    if number:
        formatted_number = number.replace(' ', '')

        # Catch any numbers that contain special chars or anything other than
        # numerical digits and '+'
        if re.match("[0-9+]*[^0-9+]+[0-9+]*", formatted_number):
            form_instance.add_error(
                    number_key,
                    'This phone number contains non numerical characters and is therefore \
not valid.')
            return formatted_number

        if '+' not in formatted_number:
            if len(formatted_number) > 11:
                form_instance.add_error(
                    number_key,
                    "This phone number is too long. It can only have a maximum \
of 11 digits without a '+'.")
            elif len(formatted_number) < 10:
                form_instance.add_error(
                    number_key,
                    "This phone number is too short. It needs a minimum \
of 10 digits without a '+'.")
        else:
            if len(formatted_number) > 13:
                form_instance.add_error(
                    number_key,
                    "This phone number is too long. It can only have a maximum \
of 13 digits with a '+'.")
            elif len(formatted_number) < 12:
                form_instance.add_error(
                    number_key,
                    "This phone number is too short. It needs a minimum \
of 12 digits with a '+'.")

        return formatted_number

    return number
