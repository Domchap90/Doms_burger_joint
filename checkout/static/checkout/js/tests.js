const{ test } = QUnit;

QUnit.module('updateSubmitBtnState', function(){   
    test('spending warning present', function(assert){
        $("#spending_warning").html(
            `<p>You still need to spend £5.00 more to be eligible to\
order online.</p>`);

        $(document).ready(updateSubmitBtnState);
        updateSubmitBtnState();

        assert.ok(
            $("#place_order_btn").hasClass('disabled') &&
            $("#place_order_btn").is(':disabled'),
            "checkout button is disabled and has appropriate styling");
    });

    test('spending warning absent', function(assert){
        $("#spending_warning").empty();
        $(document).ready(updateSubmitBtnState);
        updateSubmitBtnState();

        assert.ok(
            !$("#place_order_btn").hasClass('disabled') &&
            !$("#place_order_btn").is(':disabled'),
            "checkout button is enabled and has appropriate styling");
    });
});

QUnit.module('Form submission', function(hook){

    test('isFormValid function:', function(assert){
        $("#test_submit_button").trigger('click');

        $.mockjax({
            type: 'POST',
            url: `is_form_valid/false/`,
        });

        const expectedDataToValidate = {
            "name": "James",
            "mobile_number": "07771 777 666",
            "email": "test@domain.co.uk",
            "csrfmiddlewaretoken": "csrf_123",
            "address_line1": "101 test rd",
            "address_line2": "London",
            "postcode": "S1D 3AP",
            "delivery_instructions": "Leave round the back",

        };
       
        let dataSentToValidate = $.mockjax.unmockedAjaxCalls()[0]['data'];
        assert.deepEqual(dataSentToValidate, expectedDataToValidate,
            'ajax call sends correct form data');

    });

});
