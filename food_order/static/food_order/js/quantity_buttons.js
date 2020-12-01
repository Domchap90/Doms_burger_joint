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
const itemUpperQtyLimit = 10;
const comboUpperQtyLimit = 5;
const comboTwoUpperQtyLimit = 3;
const lowerQtyLimit = 1;

function updateCheckoutBtnState() {
    if($('#spending_warning').children().length>0) {
        $(".checkout-btn").addClass('disabled');
        $(".checkout-btn").prop('disabled', true);
    } else {
        $(".checkout-btn").removeClass('disabled');
        $(".checkout-btn").prop('disabled', false);
    }
}

function updateBtnState() {
    activateAllButtons();
    let combos = $(".order-combo-container .item-container").children();
    let sum_combo_items_1 = 0;
    let sum_combo_items_2 = 0;
    let sum_combo_items_3 = 0;
    updateCheckoutBtnState();

    // Evaluate sum of combo items for each id
    for(combo of combos) {
        let comboQty = $(combo).find('.order-qty');

        // First check that quantity area belongs to a combo
        if (comboQty.length>0) {
            // Then sum combos with identical ids.
            combo_val = parseInt(comboQty.children('input').val());
            
            if (comboQty.children('input').attr('id').split('_')[1]=='1') {
                sum_combo_items_1 += combo_val;
            } else if (comboQty.children('input').attr('id').split('_')[1]=='2') {
                sum_combo_items_2 += combo_val;
            } else {
                sum_combo_items_3 += combo_val;
            }
        }
    }
    let items = $('.item-container').children();
    let allItems = items.append(combos);

    // Evaluate state of +/- buttons for each qty area using the sum of combos from above.
    for(item of allItems) {
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
        } else { 
        // Case where quantity value is moving down from upper limit.
            if ($(quantityObj).find('.add i').hasClass('disabled')){
                $(quantityObj).find('.add i').removeClass('disabled');
            }
        }
        
        // Disables remove button for item lower limit
        if(quantityObj.children('input').val()==lowerLimit){
            $(quantityObj).find('.remove span').addClass('disabled');
        } else { 
        // Case where quantity value is moving up from lower limit.
            if ($(quantityObj).find('.remove span').hasClass('disabled')){
                $(quantityObj).find('.remove span').removeClass('disabled');
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

        // Where combo qty input boxes sum to upper limit, disable add buttons for corresponding combos.
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

        // Qty input box is equal to lower limit, disable remove button.
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
            if (typeOfItem == 'combo') {
                $('#comborow_'+comboHashKey+' .order-combo-subtotal').html('£'+subtotal);
            } else {
                $('#itemrow_'+itemID+' div:nth-child(4)').html('£'+subtotal);
            }
            $('#'+itemQtyId).val(newQtyVal);

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
                $('#spending_warning').html(`<p>You still need to spend £`+remaining_spend.toFixed(2)+` more to be eligible for delivery.</p>`);
                $('.checkout-btn').prop("disabled", true);
                $('.checkout-btn').addClass('disabled');
            } else {
                $('.checkout-btn').prop('disabled', false);
                if ($('.checkout-btn').hasClass('disabled')){
                    $('.checkout-btn').removeClass('disabled');
                }
                // let proceedBtn = document.getElementById('proceed-checkout-link');
                // $(proceedBtn).attr("href", "/checkout/collect_or_delivery/");
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
    // Prevents qty buttons from being spammed whilst ajax calls are made
    let buttons = document.getElementsByTagName('button');
    Array.from(buttons).forEach( button => {
        $(button).prop('disabled', true);
    });
}

function activateAllButtons() {
    // Allows buttons to be pressed after server has finished dealing with request
    let buttons = document.getElementsByTagName('button');

    Array.from(buttons).forEach( button => {
        $(button).prop('disabled', false);
    });
}
