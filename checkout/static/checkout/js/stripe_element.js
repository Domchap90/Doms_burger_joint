// Global vars
const stripePublicKey = $("#id_stripe_public_key").text().slice(1,-1);
const stripeClientSecret = $("#id_client_secret").text().slice(1,-1);
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements({
    fonts: [
        {
            cssSrc: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400&display=swap',
        },
    ],
});
const form = document.getElementById('payment-form');
const isCollection = ($('input[name="for_collection"]').val() == 'True') ? true : false;
const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

const style = {
    base: {
        color: "#000",
        fontFamily: '"Montserrat", sans-serif',
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
            color: "#5e5e5e",
            fontFamily: "Montserrat",
        }
    },
};
const card = elements.create("card", { hidePostalCode: true, style: style });

$(document).ready(function() {
    // Stripe injects an iframe into the DOM
    card.mount("#card-element");

    updateSubmitBtnState();
});

function updateSubmitBtnState() {
    if($('#spending_warning').children().length>0) {
        $("#place-order-btn").addClass('disabled');
        $('#place-order-btn').prop('disabled', true);
    } else {
        $("#place-order-btn").removeClass('disabled');
        $('#place-order-btn').prop('disabled', false);
    }
}

card.addEventListener('change', function(event){
    $('#card-error').empty();
    if (event.error){
        $('#card-error').html(`<span class="material-icons">error</span>  ${event.error.message}`);
    } 
})

form.addEventListener('submit', validateForm());

async function validateForm(event) {
    // First stop form being submitted immediately to allow control of form submission
    event.preventDefault(); // comment out code for JS testing
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#below-nav-container').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    let isValid = false;

    // Initiate with form fields shared amongst Collection and Delivery forms
    dataToValidate = {
        'name': $.trim(form.name.value),
        'mobile_number': $.trim(form.mobile_number.value),
        'email': $.trim(form.email.value),
        'csrfmiddlewaretoken': form.csrfmiddlewaretoken.value,
    }
    // Add delivery form field information if applicable
    if (!isCollection) {
        dataToValidate['address_line1'] = $.trim(form.address_line1.value);
        dataToValidate['address_line2'] = $.trim(form.address_line2.value);
        dataToValidate['postcode'] = $.trim(form.postcode.value);
        dataToValidate['delivery_instructions'] = $.trim(form.delivery_instructions.value);
    }

    try {
        isValid = await isFormValid(dataToValidate);
    } catch(error) {
        console.log('validateForm error: '+error)
    }
    if (isValid == false) {
        $('#loading-overlay').fadeToggle(100);
        $('#below-nav-container').fadeToggle(100);
        card.update({ 'disabled': false});
        $('#place-order-btn').attr('disabled', false);
    } else {
        submitToStripe(dataToValidate);
    }
}
 
async function isFormValid(formData){
    let result = false;
    $('.field-error').empty();

    await $.ajax({
        type: 'POST',
        url: `is_form_valid/${isCollection}/`,
        data: formData,
        dataType: 'json',
        success: function(response) {
            if (response['valid']) {
                result = JSON.parse(response['valid']);
            } else {
                for (err in response) {
                    $('#'+err+'-error').append(`<p>`+response[err]+`</p>`);
                }
            }

        }
    });

    return result;
}

function submitToStripe(dataToSubmit) {
    let url = '/checkout/cached_payment_intent/'  
    const data = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': stripeClientSecret,
        'is_collection': isCollection,
    }
    let cardPaymentData = {
        payment_method: {
            card: card,
            billing_details: {
                name: dataToSubmit['name'],
                phone: dataToSubmit['mobile_number'],
                email: dataToSubmit['email'],
            }
        }
    }
    if (isCollection == false) {
        cardPaymentData['payment_method']['billing_details']['address'] = {
                    line1: dataToSubmit['address_line1'],
                    line2: dataToSubmit['address_line2'],
                    postal_code: dataToSubmit['postcode'],
        }
        cardPaymentData['shipping'] = {name: dataToSubmit['name'],};
        cardPaymentData['shipping']['address'] = {
                    line1: dataToSubmit['address_line1'],
                    line2: dataToSubmit['address_line2'],
                    postal_code: dataToSubmit['postcode'],
        }
    }

    // Send form data to the server before calling Stripe. To ensure info is not lost if user exits
    // whilst loading the success page.
    $.post(url, data).done(function() {
        stripe.confirmCardPayment(stripeClientSecret, cardPaymentData).then(function(result) {
            if (result.error) {
                // Show error to your customer (e.g., insufficient funds)
                $('#card-error').html(`<span class="material-icons">error</span> ${result.error.message}`);
                $('#below-nav-container').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                // The payment has been processed!
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit(); // comment out for testing webhooks
                }
            }
        });
    }).fail( function() {
        // main checkout window reloads with appropriate messages from django.
        location.reload();
    })
}

