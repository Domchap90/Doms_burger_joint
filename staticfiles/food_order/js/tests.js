const { test } = QUnit;

QUnit.module('Quantity buttons tests:', function() {

    QUnit.module('updateCheckoutBtnState', function() {
        test('spending warning present', function(assert) {
            // Qunit DOM is initialized with spending warning
            let checkoutVisualDisabled = $('.checkout-btn').hasClass(
                'disabled');
            let checkoutFunctionalDisabled = $('.checkout-btn').is(
                ':disabled');
            assert.ok(
                checkoutVisualDisabled && checkoutFunctionalDisabled,
                "button is disabled");
        });

        test('spending warning absent', function(assert) {
            $('#spending_warning').empty();
            /* recall initial function in doc ready to recognise changed
            spending warning */
            $(document).ready(updateCheckoutBtnState);
            updateCheckoutBtnState();

            let checkoutVisualDisabled = $('.checkout-btn').hasClass(
                'disabled');
            let checkoutFunctionalDisabled = $('.checkout-btn').is(
                ':disabled');
            assert.ok(
                checkoutVisualDisabled==false &&
                checkoutFunctionalDisabled==false,
                "button is enabled");
        });
        
    });

    QUnit.module('Doc ready state:', function() {

        test('Upper limit reached', function(assert) {            
            let addBtns = $('.qty-btn.add').children();
            let minusBtns = $('.qty-btn.remove').children();

            for (btn of addBtns){
                let btnParentId = $(btn).parent().attr('id');
                assert.ok(
                    $(btn).hasClass('disabled'), 'add button "'+
                    btnParentId+'" disabled');
            }

            for (btn of minusBtns){
                let btnParentId = $(btn).parent().attr('id');
                assert.ok(
                    $(btn).hasClass('disabled') == false,
                    'minus button "'+btnParentId+'" still enabled');
            }         
        });

        test('Lower limit reached', function(assert) {
            // Quantity values changed in DOM, to reach lower limits
            $('.order-qty-input').val('1');
            
            // Called within document ready, so no need to trigger any events
            $(document).ready(updateBtnState);
            updateBtnState();         

            let addBtns = $('.qty-btn.add').children();
            let minusBtns = $('.qty-btn.remove').children();

            for (btn of addBtns){
                let btnParentId = $(btn).parent().attr('id');
                assert.ok($(btn).hasClass('disabled') == false, 'add button "'+
                          btnParentId+'" still enabled');
            }

            for (btn of minusBtns){
                let btnParentId = $(btn).parent().attr('id');
                assert.ok($(btn).hasClass('disabled'), 'minus button "'+
                          btnParentId+'" disabled');
            }
        });

        test('Inbetween limits', function(assert) {
            // Quantity values changed in DOM, to reach lower limits
            $('#item_7_qty').val('9');
            $('#combo_1_c123_qty').val('4');
            $('#combo_2_c278_qty').val('2');
            $('#combo_3_c369_qty').val('2');
            $('#combo_3_c379_qty').val('2');
            
            // Called within document ready, so no need to trigger any events
            $(document).ready(updateBtnState);
            updateBtnState();         

            let addBtns = $('.qty-btn.add').children();
            let minusBtns = $('.qty-btn.remove').children();

            for (btn of addBtns){
                let btnParentId = $(btn).parent().attr('id');
                assert.ok(
                    $(btn).hasClass('disabled') == false,
                    'add button "'+btnParentId+'" enabled');
            }

            for (btn of minusBtns){
                let btnParentId = $(btn).parent().attr('id');
                assert.ok(
                    $(btn).hasClass('disabled') == false,
                    'minus button "'+btnParentId+'" enabled');
            }
        });
        
    });

    QUnit.module('Change Quantity Controls:', function(hook) {
        hook.afterEach( function() {
            $.mockjax.clear();
            // reset values
            $('#item_7_qty').val('10');
            $('#combo_3_c369_qty').val('3');
            $('#combo_3_c379_qty').val('2');

            // reset subtotals
            $('#itemrow_7 .subtotal').html('£100');
            $('#comborow_c123 .order-combo-subtotal').html('£100');
            $('#comborow_c278 .order-combo-subtotal').html('£90');
            $('#comborow_c369 .order-combo-subtotal').html('£120');
            $('#comborow_c379 .order-combo-subtotal').html('£80');

            // reset totals
            $('#total').html('£490.00');
            $('#grand_total').html(`£491.99`);

            // ensure checkout button is disabled
            if (!$('.checkout-btn').hasClass('disabled'))
                $('.checkout-btn').addClass('disabled');

            // Render button states for settings above
            $(document).ready(updateBtnState);
            updateBtnState(); 
        });

        test("attempt to increase quantity on upper limit", function(assert) {
            // Setup values to equal their upper limits
            $('#item_7_qty').val('10');
            $('#combo_3_c369_qty').val('2');
            $('#combo_3_c379_qty').val('3');

            $(document).ready(updateBtnState);
            updateBtnState();   

            assert.expect(5);
            let done = assert.async();

            $('#item_7_add').trigger('click');
            $('#combo_3_c379_add').trigger('click');

            // Totals unchanged
            $.mockjax({
                type: 'POST',
                url: `edit_item/item/7/`,
            });

            setTimeout( function(){
                assert.ok(
                    $('#item_7_qty').val() == '10' &&
                    $('#combo_3_c379_qty').val() == '3',
                    'values remain the same');
            
                assert.ok(
                    $('#item_7_add').children().hasClass('disabled') &&
                    $('#combo_3_c379_add').children().hasClass('disabled'),
                    'add buttons remain disabled');

                assert.ok(
                    $.mockjax.unmockedAjaxCalls()==false,
                    "Backend isn't called to update database");

                assert.ok(
                    $('#itemrow_7 .subtotal').html()=='£100' &&
                    $('#comborow_c379 .order-combo-subtotal').html()=='£80',
                    "subtotals unchanged");

                assert.ok(
                    $('#grand_total').html()=='£491.99',
                    'grand total unchanged');
                done();
            });

        }); 

        test("attempt to increase combo quantity below upper limit",
             function(assert) {
            $('#combo_3_c369_qty').val('2');
            $('#combo_3_c379_qty').val('1');
            $('#comborow_c369 .order-combo-subtotal').html(`£80.00`);
            $('#comborow_c379 .order-combo-subtotal').html(`£40.00`);
            $('#total').html('£410.00');
            $('#grand_total').html(`£411.99`);

            $(document).ready(updateBtnState);
            updateBtnState();

            assert.expect(4);
            let done = assert.async();

            $('#combo_3_c379_add').trigger('click');

            const expectedComboData = {
                newQtyVal: 2,
                oldQtyVal: "1",
                comboHashKey: 'c379',
                csrfmiddlewaretoken: "csrf_test"
            }
            
            $.mockjax({
                type: 'POST',
                url: `edit_item/combo/c379/`,
                responseText: {
                    "subtotal": 80.00,
                    "subtotal_change": 40.00,
                }
            });

             $.ajax({
                type: 'POST',
                url: `edit_item/combo/c379/`,
                success: function(response) {
                    let typeOfItem = 'combo';
                    let itemID = '3';
                    let itemQtyId = 'combo_3_c379_qty';
                    let newQtyVal = 2;
                    let comboHashKey = 'c379';

                    // receives subtotal from backend and updates total values
                    let subtotal = JSON.parse(response['subtotal']);
                    subtotal_change = JSON.parse(response['subtotal_change']);

                    if (typeOfItem == 'combo') {
                        $('#comborow_'+comboHashKey+
                        ' .order-combo-subtotal').html('£'+subtotal);
                    } else {
                        $('#itemrow_'+itemID+
                        ' div:nth-child(4)').html('£'+subtotal);
                    }
                    $('#'+itemQtyId).val(newQtyVal);
                    
                    updateTotals(subtotal_change);
                }
            });

            setTimeout( function() {
                assert.deepEqual(
                    $.mockjax.unmockedAjaxCalls()[0]['data'],
                    expectedComboData,
                    'updateQty posts correct combo data to backend.');

                assert.ok(
                    $('#combo_3_c379_qty').val()==2,
                    "combo value increments by 1");

                assert.ok(
                    $('#grand_total').html()=='£451.99' &&
                    $('#comborow_c379 .order-combo-subtotal').html()=='£80',
                    "subtotal and total are updated correctly.");

                // Check both combos of type 3 have all their buttons enabled as 
                // sum of values < upperlimit & each value > lower limit
                assert.ok(
                    $('#item__3_c369_add').children().hasClass(
                        'disabled')==false &&
                    $('#item__3_c369_remove').children().hasClass(
                        'disabled')==false &&
                    $('#item__3_c379_add').children().hasClass(
                        'disabled')==false &&
                    $('#item__3_c379_remove').children().hasClass(
                        'disabled')==false,
                    "add & minus buttons enabled for 2 combos of same type\
                    between limits")

                done();
            },500);
        });

        test("attempt to increase item quantity below upper limit",
             function(assert) {
            // Setup values and totals
            $('#item_7_qty').val('9');
            $('#itemrow_7 .subtotal').html(`£90.00`);
            $('#total').html('£480.00');
            $('#grand_total').html(`£481.99`);
            $(document).ready(updateBtnState);
            updateBtnState();   
            
            assert.expect(4);
            let done = assert.async();

            $('#item_7_add').trigger('click');

            const expectedItemData = {
                newQtyVal: 10,
                oldQtyVal: "9",
                csrfmiddlewaretoken: "csrf_test"
            }
            $.mockjax({
                type: 'POST',
                url: `edit_item/item/7/`,
                responseText: {
                    "subtotal": 100.00,
                    "subtotal_change": 10.00,
                }
            });

            $.ajax({
                type: 'POST',
                url: `edit_item/item/7/`,
                success: function(response) {
                    let typeOfItem = 'item';
                    let itemID = '7';
                    let itemQtyId = 'item_7_qty';
                    let newQtyVal = 10;
                    let comboHashKey = null;

                    // receives subtotal from backend and updates total values
                    let subtotal = JSON.parse(response['subtotal']);
                    subtotal_change = JSON.parse(response['subtotal_change']);

                    if (typeOfItem == 'combo') {
                        $('#comborow_'+comboHashKey+
                            ' .order-combo-subtotal').html('£'+subtotal);
                    } else {
                        $('#itemrow_'+itemID+
                            ' div:nth-child(4)').html('£'+subtotal);
                    }
                    $('#'+itemQtyId).val(newQtyVal);

                    updateTotals(subtotal_change);
                }
            });
            
            setTimeout( function(){
                assert.deepEqual(
                    $.mockjax.unmockedAjaxCalls()[0]['data'],
                    expectedItemData,
                    'updateQty posts correct item data to backend.');

                assert.ok($('#item_7_qty').val()==10,
                         "item value increments by 1");

                assert.ok(
                    $('#grand_total').html()=='£491.99' &&
                    $('#itemrow_7 .subtotal').html()=='£100',
                    "subtotal and total are updated correctly.");

                assert.ok(
                    $('#item_7_add').children().hasClass('disabled') &&
                    $('#item_7_remove').children().hasClass('disabled')==false,
                    "add button disabled, minus button enabled");
                
                done();
            },500);

        }); 

        test("attempt to decrease quantity on lower limit", function(assert) {
            // Setup values to equal their lower limits
            $('#item_7_qty').val('1');
            $('#itemrow_7 .subtotal').html('£10');
            $('#combo_3_c369_qty').val('1');
            $('#combo_3_c379_qty').val('1');
            $('#comborow_c369 .order-combo-subtotal').html('£40');
            $('#comborow_c379 .order-combo-subtotal').html('£40');
            $('#total').html('£280.00');
            $('#grand_total').html(`£281.99`);

            $(document).ready(updateBtnState);
            updateBtnState();   

            assert.expect(5);
            let done = assert.async();

            $('#item_7_remove').trigger('click');
            $('#combo_3_c379_remove').trigger('click');

            $.mockjax({
                type: 'POST',
                url: `edit_item/item/7/`,
            });

            setTimeout( function(){
                assert.ok(
                    $('#item_7_qty').val() == '1' &&
                    $('#combo_3_c379_qty').val() == '1',
                    'values remain the same')
         
                assert.ok(
                    $('#item_7_remove').children().hasClass('disabled') &&
                    $('#combo_3_c379_remove').children().hasClass('disabled'),
                    'minus buttons remain disabled')

                assert.ok($.mockjax.unmockedAjaxCalls()==false,
                         "Backend isn't called to update database");

                assert.ok(
                    $('#itemrow_7 .subtotal').html()=='£10' &&
                    $('#comborow_c379 .order-combo-subtotal').html()=='£40',
                    "subtotals unchanged");

                assert.ok(
                    $('#grand_total').html()=='£281.99',
                    'grand total unchanged');
                done();
            });

        }); 

        test("attempt to decrease combo quantity above lower limit",
             function(assert) {
            // Using initial totals and qty values on qunit DOM 

            $(document).ready(updateBtnState);
            updateBtnState();

            assert.expect(4);
            let done = assert.async();

            $('#combo_3_c379_remove').trigger('click');

            const expectedComboData = {
                newQtyVal: 1,
                oldQtyVal: "2",
                comboHashKey: 'c379',
                csrfmiddlewaretoken: "csrf_test"
            }
            
            $.mockjax({
                type: 'POST',
                url: `edit_item/combo/c379/`,
                responseText: {
                    "subtotal": 40.00,
                    "subtotal_change": -40.00,
                }
            });

             $.ajax({
                type: 'POST',
                url: `edit_item/combo/c379/`,
                success: function(response) {
                    let typeOfItem = 'combo';
                    let itemID = '3';
                    let itemQtyId = 'combo_3_c379_qty';
                    let newQtyVal = 1;
                    let comboHashKey = 'c379';
   
                    // receives subtotal from backend and updates total values
                    let subtotal = JSON.parse(response['subtotal']);
                    subtotal_change = JSON.parse(response['subtotal_change']);

                    if (typeOfItem == 'combo') {
                        $('#comborow_'+comboHashKey+
                            ' .order-combo-subtotal').html('£'+subtotal);
                    } else {
                        $('#itemrow_'+itemID+
                            ' div:nth-child(4)').html('£'+subtotal);
                    }
                    $('#'+itemQtyId).val(newQtyVal);
                    
                    updateTotals(subtotal_change);
                }
            });

            setTimeout( function() {
                assert.deepEqual(
                    $.mockjax.unmockedAjaxCalls()[0]['data'],
                    expectedComboData,
                    'updateQty posts correct combo data to backend.');

                assert.ok(
                    $('#combo_3_c379_qty').val()==1,
                    "combo value decreases by 1");

                assert.ok(
                    $('#grand_total').html()=='£451.99' &&
                    $('#comborow_c379 .order-combo-subtotal').html()=='£40',
                    "subtotal and total are updated correctly.");

                /* Check combos of type 3 have correct button states according
                to their limits */
                assert.ok(
                    $('#combo_3_c369_add').children().hasClass(
                        'disabled')==false &&
                    $('#combo_3_c369_remove').children().hasClass(
                        'disabled')==false &&
                    $('#combo_3_c379_add').children().hasClass(
                        'disabled')==false &&
                    $('#combo_3_c379_remove').children().hasClass(
                        'disabled'),
                    "all buttons enabled, except for case where lower limit\
                    of 1 reached")

                done();
            },1000);

        }); 

         test("attempt to decrease item quantity above lower limit",
              function(assert) {
            // Setup values and totals
            $(document).ready(updateBtnState);
            updateBtnState();   
            
            assert.expect(4);
            let done = assert.async();

            $('#item_7_remove').trigger('click');

            const expectedItemData = {
                newQtyVal: 9,
                oldQtyVal: "10",
                csrfmiddlewaretoken: "csrf_test"
            }
            $.mockjax({
                type: 'POST',
                url: `edit_item/item/7/`,
                responseText: {
                    "subtotal": 90.00,
                    "subtotal_change": -10.00,
                }
            });

            $.ajax({
                type: 'POST',
                url: `edit_item/item/7/`,
                success: function(response) {
                    let typeOfItem = 'item';
                    let itemID = '7';
                    let itemQtyId = 'item_7_qty';
                    let newQtyVal = 9;
                    let comboHashKey = null;

                    // receives subtotal from backend and updates total values
                    let subtotal = JSON.parse(response['subtotal']);
                    subtotal_change = JSON.parse(response['subtotal_change']);

                    if (typeOfItem == 'combo') {
                        $('#comborow_'+comboHashKey+
                            ' .order-combo-subtotal').html('£'+subtotal);
                    } else {
                        $('#itemrow_'+itemID+
                            ' div:nth-child(4)').html('£'+subtotal);
                    }
                    $('#'+itemQtyId).val(newQtyVal);

                    updateTotals(subtotal_change);
                }
            });
            
            setTimeout( function(){
                assert.deepEqual(
                    $.mockjax.unmockedAjaxCalls()[0]['data'], expectedItemData,
                    'updateQty posts correct item data to backend.');

                assert.ok($('#item_7_qty').val()==9, "item value decreases by 1");

                assert.ok(
                    $('#grand_total').html()=='£481.99' &&
                    $('#itemrow_7 .subtotal').html()=='£90',
                    "subtotal and total are updated correctly.");

                assert.ok(
                    $('#item_7_add').children().hasClass('disabled')==false &&
                    $('#item_7_remove').children().hasClass('disabled')==false,
                    "both buttons enabled");
                
                done();
            },500);

        }); 
    });
});
