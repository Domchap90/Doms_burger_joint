var stripePublicKey = $("#id_stripe_public_key").text().slice(1,-1);
var stripeClientSecret = $("#id_client_secret").text().slice(1,-1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var card = elements.create("card", { style: style });
// Stripe injects an iframe into the DOM
card.mount("#card-element");

var style = {
      base: {
        color: "#32325d",
        fontFamily: "'Montseratt', sans-serif",
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
            color: '#aab7c4',
            fontFamily: 'Montserrat, sans-serif',
        }
      },
      invalid: {
        fontFamily: "'Montseratt', sans-serif",
        color: "#fa755a",
      }
    };

card.addEventListener('change', function(event){
    $('#card-error').empty();
    if (event.error){
        $('#card-error').html(`<span class="material-icons">error</span>  ${event.error.message}`);
    } 
})

var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#below-nav-container').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();  
    var url = '/checkout/cached_payment_intent/'  
    var data = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': stripeClientSecret,

    }
    // Send form data to the server before calling Stripe. To ensure info is not lost if user cancels
    // whilst loading the success page.
    $.post(url, data).done(function() {
        stripe.confirmCardPayment(stripeClientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.name.value),
                    phone: $.trim(form.mobile_number.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.address_line1.value),
                        line2: $.trim(form.address_line2.value),
                        postal_code: $.trim(form.postcode.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.name.value),
                address: {
                    line1: $.trim(form.address_line1.value),
                    line2: $.trim(form.address_line2.value),
                    postal_code: $.trim(form.postcode.value),
                }
            }
        }).then(function(result) {
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
                    form.submit();
            }
            }
        });
    }).fail( function() {
        // main checkout window reloads with appropriate messages from django.
        location.reload();
    })
});

