$(document).ready(function(){
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
    let items = $(".item_container").children();
    updateCheckoutBtnState();
    for(item of items) {
        let itemQty = $(item).find('.order-qty');
        
        if (itemQty.length>0) {
            let itemQtyInputId = itemQty.children('input').attr('id');
            if (itemQtyInputId.includes("item")) {
                changeBtnState(itemQty, lowerQtyLimit , itemUpperQtyLimit);
            } else if (itemQtyInputId.includes("combo_2")) {
                console.log('combo_2 updateBtnState accesed.')
                changeBtnState(itemQty, lowerQtyLimit , comboTwoUpperQtyLimit);
            } else {
                changeBtnState(itemQty, lowerQtyLimit , comboUpperQtyLimit);
            }
        }
    }
}

function changeBtnState(quantityObj, lowerLimit , upperLimit) {
    if (quantityObj.children('input').val()==upperLimit) {
        $(quantityObj).find('.add i').addClass('disabled');
    } else if(quantityObj.children('input').val()==lowerLimit){
        $(quantityObj).find('.remove span').addClass('disabled');
    } 
    // Deals with case where quantity value is moving away from the limits.
    else { 
        console.log('between limits accesed.')
        if ($(quantityObj).find('button > *').hasClass('disabled')){
            $(quantityObj).find('button > *').removeClass('disabled');
        }
    }
}

function increaseQuantity(selectedQuantityBtn){
    console.log('increase quantity function accessed')
    let typeOfItem = selectedQuantityBtn.id.split("_")[0];
    let itemID = selectedQuantityBtn.id.split("_")[1];
    let itemQtyId = typeOfItem+'_'+itemID+"_qty";
    console.log('typeOfItem = '+typeOfItem+'itemID = '+itemID+'itemQtyId = '+itemQtyId)
    if (typeOfItem == 'combo') {
        let comboHashKey = selectedQuantityBtn.id.split("_")[2]; 
        itemQtyId = typeOfItem+'_'+itemID+'_'+comboHashKey+"_qty";
    }
    let qtyValue = $('#'+itemQtyId).val();
    // Apply constraints on quantities, depending on upper order limits as set above in global vars.
    if (typeOfItem==='item' && qtyValue<itemUpperQtyLimit) {
        qtyValue = parseInt(qtyValue)+1;
        updateQty(itemQtyId, qtyValue);
    } else if (typeOfItem==='combo' && itemID==2 && qtyValue<comboTwoUpperQtyLimit) {
        qtyValue = parseInt(qtyValue)+1;
        updateQty(itemQtyId, qtyValue);
    } else if (typeOfItem==='combo' && itemID!=2 && qtyValue<comboUpperQtyLimit){
        qtyValue = parseInt(qtyValue)+1;
        updateQty(itemQtyId, qtyValue);
    }
    
    $('#'+itemQtyId).val(qtyValue);
    updateBtnState();
}

function decreaseQuantity(selectedQuantityBtn){
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
        qtyValue = parseInt(qtyValue)-1;
        updateQty(itemQtyId, qtyValue);
    }
    $('#'+itemQtyId).val(qtyValue);
    updateBtnState();
}

function updateQty(itemQtyId, qtyVal) {
    // Adjusts the quantity server side via an ajax call.
    // let csrfToken = "{{ csrf_token }}";
    let typeOfItem = itemQtyId.split('_')[0];
    let itemID = itemQtyId.split('_')[1];
    let itemData = {
                    'qtyVal': qtyVal,
                    'csrfmiddlewaretoken': csrfToken
                    };
    if (typeOfItem == 'combo') {
        let comboHashKey = itemQtyId.split('_')[2];
        itemData['comboHashKey'] = comboHashKey;
    }
    $.ajax({
        type: 'POST',
        url: `edit_item/${typeOfItem}/${itemID}/`,
        data: itemData,
        dataType: 'json',
        success: function(response) {
            console.log("Quantity updated for order.")
        }
    });
}

function removeItem(itemToRemove){
    let typeOfItem = itemToRemove.id.split("_")[0];
    let itemID = itemToRemove.id.split("_")[1];
    // let csrfToken = getCookie('csrftoken');
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

