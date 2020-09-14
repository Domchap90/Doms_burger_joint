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
  $('#below-nav-container').fadeToggle(100);
  $('#loading-overlay').fadeToggle(100);
  stripe.confirmCardPayment(stripeClientSecret, {
    payment_method: {
      card: card
    }
  }).then(function(result) {
    if (result.error) {
        // Show error to your customer (e.g., insufficient funds)
        $('#card-error').html(`<span class="material-icons">error</span> ${result.error.message}`);
        $('#below-nav-container').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);
      card.update({ 'disabled': false })
    } else {
      // The payment has been processed!
      if (result.paymentIntent.status === 'succeeded') {
            form.submit();
      }
    }
  });
});

