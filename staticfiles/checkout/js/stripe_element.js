var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card_element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card_error');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment_form');

form.addEventListener('submit', function(ev) {
    console.log(`entered\n\tclientSecret = '${clientSecret}' is of type ${typeof clientSecret},\n\tstripePublicKey = ${stripePublicKey}`)
    ev.preventDefault();
    card.update({ 'disabled': true});
    $('#place_order_btn').attr('disabled', true);
    $('#payment_form').fadeToggle(100);
    $('#loading_overlay').fadeToggle(100);

    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    var url = '/checkout/cached_payment_intent/';

    $.post(url, postData).done(function () {
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.name.value),
                    phone: $.trim(form.mobile_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.address_line1.value),
                        line2: $.trim(form.address_line2.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.name.value),
                phone: $.trim(form.mobile_number.value),
                address: {
                    line1: $.trim(form.address_line1.value),
                    line2: $.trim(form.address_line2.value),
                    postal_code: $.trim(form.postcode.value),
                }
            },
        }).then(function(result) {
            console.log('then function entered')
            if (result.error) {
                var errorDiv = document.getElementById('card_error');
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                $('#payment_form').fadeToggle(100);
                $('#loading_overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#place_order_btn').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    console.log('success reached')
                    // form.submit();
                }
            }
        });
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    })
});