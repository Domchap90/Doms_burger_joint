$(document).ready(function(){
        window.addEventListener( "pageshow", function ( event ) {
            // Determines if page was reloaded using bf cache and
            // reloads from server to retrieve correct context data.
		    var loadedFromCache = event.persisted ||
		    ( typeof window.performance != "undefined" && 
              window.performance.navigation.type === 2 );

            if ( loadedFromCache ) {
                // Handle page restore.
                window.location.reload();
            }
		});
        updateBtnState();
        updateCheckoutBtnState();
    }, {passive: true});
// Make event listener passive to improve performance (wheel scroll element).
var itemUpperQtyLimit = 10;
var comboUpperQtyLimit = 5;
var comboTwoUpperQtyLimit = 3;
var lowerQtyLimit = 1;

function updateCheckoutBtnState() {
    if($('#spending_warning').children().length>0) {
        $(".checkout-btn").addClass('disabled');
    } else {
        $(".checkout-btn").removeClass('disabled');
    }
}

function updateBtnState() {
    activateAllButtons();
    let items = $(".item_container").children();
    sum_combo_items_1 = 0;
    sum_combo_items_2 = 0;
    sum_combo_items_3 = 0;
    updateCheckoutBtnState();

    // Evaluate sum of combo items for each id
    for(item of items) {
        let itemQty = $(item).find('.order-qty');
        // First check that quantity area belongs to a combo
        if (itemQty.length>0 && itemQty.children('input').attr('id').split('_')[0]=='combo') {
            // Then sum combos with identical item ids.
            combo_val = parseInt(itemQty.children('input').val());
            if (itemQty.children('input').attr('id').split('_')[1]=='1') {
                sum_combo_items_1 += combo_val;
            } else if (itemQty.children('input').attr('id').split('_')[1]=='2') {
                sum_combo_items_2 += combo_val;
            } else {
                sum_combo_items_3 += combo_val;
            }
        }
    }

    // Evaluate state of +/- buttons for each qty area using the sum of combos from above.
    for(item of items) {
        let itemQty = $(item).find('.order-qty');
        // Check Qty area contains at least 1 element/button to be valid
        if (itemQty.length>0) {
            let itemQtyInputId = itemQty.children('input').attr('id');
            if (itemQtyInputId.includes("item")) {
                changeBtnState(itemQty, 0, lowerQtyLimit , itemUpperQtyLimit);
            } else if (itemQtyInputId.includes("combo_2")) {
                changeBtnState(itemQty, sum_combo_items_2, lowerQtyLimit , comboTwoUpperQtyLimit);
            } else if (itemQtyInputId.includes("combo_1")){
                changeBtnState(itemQty, sum_combo_items_1, lowerQtyLimit , comboUpperQtyLimit);
            } else {
                changeBtnState(itemQty, sum_combo_items_3, lowerQtyLimit , comboUpperQtyLimit);
            }
        }
    }
}

function changeBtnState(quantityObj, sum_combo_items, lowerLimit , upperLimit) {
    // handles item qty button states
    if (quantityObj.children('input').attr('id').split('_')[0]=='item') {
        // Disables add button for item upper limit
        if (quantityObj.children('input').val()==upperLimit) {
            $(quantityObj).find('.add i').addClass('disabled');
        } // Disables remove button for item lower limit
         else if(quantityObj.children('input').val()==lowerLimit){
            $(quantityObj).find('.remove span').addClass('disabled');
        } 
        // Deals with case where quantity value is moving away from the limits.
        else { 
            if ($(quantityObj).find('button > *').hasClass('disabled')){
                $(quantityObj).find('button > *').removeClass('disabled');
            }
        }
    } else { 
        // handles combo qty button states
        combo_inputs = []
        // Gather combos of same id into list in order to iterate through list with appropriate limit.
        for (input of $('.order-combo-container .order-qty-input')) {
            if (input.id.split('_')[1] == quantityObj.children('input').attr('id').split('_')[1]) {
                combo_inputs.push(quantityObj);
            }
        }

        // if value in Qty input box is equal to upper limit, disable add button.
        if (sum_combo_items == upperLimit) {
            for (combo_input of combo_inputs) { 
                $(combo_input).find('.add i').addClass('disabled'); 
            }
        }
        // Otherwise ensure the add button is enabled.
        else {
            for (combo_input of combo_inputs) { 
                if ( $(combo_input).find('.add i').hasClass('disabled')) {
                    $(combo_input).find('.add i').removeClass('disabled'); 
                }
            }
        }

        // if value in Qty input box is equal to lower limit, disable remove button.
        if (quantityObj.children('input').val()==lowerLimit) {
            $(quantityObj).find('.remove span').addClass('disabled');
        } 
        // Otherwise ensure the remove button is enabled.
        else {
            for (combo_input of combo_inputs) {
                if ($(combo_input).find('.remove span').hasClass('disabled')) {
                    $(combo_input).find('.remove span').removeClass('disabled');
                }
            }
        }
    }
}

function increaseQuantity(selectedQuantityBtn){
    deactivateAllButtons();
    let typeOfItem = selectedQuantityBtn.id.split("_")[0];
    let itemID = selectedQuantityBtn.id.split("_")[1];
    let itemQtyId = typeOfItem+'_'+itemID+"_qty";
    // Account for combo add button ids having a different structure.
    if (typeOfItem == 'combo') {
        let comboHashKey = selectedQuantityBtn.id.split("_")[2]; 
        itemQtyId = typeOfItem+'_'+itemID+'_'+comboHashKey+"_qty";
    }
    let qtyValue = $('#'+itemQtyId).val();
    // Only allow quantity to be increased when the button is not disabled (from updateBtnState).
    if (!$(selectedQuantityBtn).children().hasClass('disabled')) {
        let oldQtyValue = qtyValue;
        qtyValue = parseInt(qtyValue)+1;
        updateQty(itemQtyId, qtyValue, oldQtyValue);
    }
    
    // $('#'+itemQtyId).val(qtyValue);
    // updateBtnState();
}

function decreaseQuantity(selectedQuantityBtn){
    deactivateAllButtons();
    let typeOfItem = selectedQuantityBtn.id.split("_")[0];
    let itemID = selectedQuantityBtn.id.split("_")[1];
    let itemQtyId = typeOfItem+'_'+itemID+"_qty";

    if (typeOfItem == 'combo') {
        let comboHashKey = selectedQuantityBtn.id.split("_")[2]; 
        itemQtyId = typeOfItem+'_'+itemID+'_'+comboHashKey+"_qty";
    }
    let qtyValue = $('#'+itemQtyId).val();
    // Apply constraints on quantities, all have same lower limit of 1.
    if (qtyValue>lowerQtyLimit) {
        let oldQtyValue = qtyValue;
        qtyValue = parseInt(qtyValue)-1;
        updateQty(itemQtyId, qtyValue, oldQtyValue);
    }
    // $('#'+itemQtyId).val(qtyValue);
    // updateBtnState();
}

function updateQty(itemQtyId, newQtyVal, oldQtyVal) {
    // Adjusts the quantity server side via an ajax call.
    let typeOfItem = itemQtyId.split('_')[0];
    let itemID = itemQtyId.split('_')[1];
    let comboHashKey = '';
    let itemData = {
                    'newQtyVal': newQtyVal,
                    'oldQtyVal': oldQtyVal,
                    'csrfmiddlewaretoken': csrfToken
                    };
    if (typeOfItem == 'combo') {
        comboHashKey = itemQtyId.split('_')[2];
        itemData['comboHashKey'] = comboHashKey;
    }
    var subtotal_change = 0;
    $.ajax({
        type: 'POST',
        url: `edit_item/${typeOfItem}/${itemID}/`,
        data: itemData,
        dataType: 'json',
        success: function(response) {
            // receives subtotal from backend and updates total values
            let subtotal = JSON.parse(response['subtotal']);
            subtotal_change = JSON.parse(response['subtotal_change']);
            // console.log('subtotal is '+subtotal)
            if (typeOfItem == 'combo') {
                $('#comborow_'+comboHashKey+' .order-combo-subtotal').html('£'+subtotal);
            } else {
                $('#itemrow_'+itemID+' div:nth-child(4)').html('£'+subtotal);
            }
            $('#'+itemQtyId).val(newQtyVal);
            // updateBtnState();
            updateTotals(subtotal_change);
        }
    });
    
}

function updateTotals(changedByAmount) {
    let updateTotal = parseFloat($('#total').html().slice(1))+changedByAmount;
    let deliveryFee = parseFloat($('#delivery_fee').html().slice(1));
    $('#total').html('£'+updateTotal.toFixed(2));

    let grandTotal = updateTotal+deliveryFee;
    $('#grand_total').html('£'+grandTotal.toFixed(2));
    updateBtnState();
    updateRemainingSpend(updateTotal);
}

function updateRemainingSpend(newTotal) {
    // Updates the warning about how much the user needs to spend in order to qualify for delivery
    $('#spending_warning').empty();
    $.ajax({
        type: 'GET',
        url: `recalculate_remaining_delivery_amount/`,
        data: {'total': newTotal},
        dataType: 'json',
        success: function(response) {
            let remaining_spend = JSON.parse(response['remaining_delivery_amount']);
            if (remaining_spend > 0) {
                $('#spending_warning').html(`<p>You still need to spend £`+remaining_spend+` more to be eligible for delivery.</p>`);
                document.getElementById('proceed-checkout-link').removeAttribute("href");
                $('.checkout-btn').addClass('disabled');
            } else {
                $('.checkout-btn').prop('disabled', false);
                let proceedBtn = document.getElementById('proceed-checkout-link');
                proceedBtn.setAttribute("href", "/checkout/collect_or_delivery/");
            }
        }
    });
    $('.checkout-btn').prop('disabled', true);
    updateCheckoutBtnState();
}

function removeItem(itemToRemove){
    // Removes item via call to server.
    let typeOfItem = itemToRemove.id.split("_")[0];
    let itemID = itemToRemove.id.split("_")[1];
    let data = {'csrfmiddlewaretoken': csrfToken}
    if (typeOfItem == 'combo') {
        let comboHashKey = itemToRemove.id.split('_')[2];
        data['comboHashKey'] = comboHashKey;
    }
    
    let url = `/food_order/remove/${typeOfItem}/${itemID}/`;
    $.post(url, data)
    .done( function() {
        location.reload();
    });
    updateCheckoutBtnState();
}

function deactivateAllButtons() {
    let buttons = document.getElementsByTagName('button');
    Array.from(buttons).forEach( button => {
        $(button).prop('disabled', true);
    });
}

function activateAllButtons() {
    let buttons = document.getElementsByTagName('button');

    Array.from(buttons).forEach( button => {
        $(button).prop('disabled', false);
    });
}