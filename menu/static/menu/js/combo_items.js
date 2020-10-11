$(document).ready(function(){
    $('select').formSelect();
    $('.collapsible').collapsible();
});

function validateComboForm(form) {
    // Notifies user that all form fields have to be selected in order to send the form.
    $('.form-error').html('');
    addComboForm = document.forms["add_combo"];
    for (field of addComboForm) {
        if ($(field).prop('required') && field.value=='') {
            $('.form-error#err-'+form).html(`<p>Please select all food options to add the combo to your order.</p>`);
        }
    }
}

function updateComboSelection(selectedItem){
    let selectedID = selectedItem.value;
    let combo_category = selectedItem.id;
    console.log('selectedID = '+selectedID+' combo_category = '+combo_category)
    let itemData = {
        'food_id': selectedID
    }

    $.ajax({
        type: 'GET',
        url: 'item/',
        data: itemData,
        dataType: 'json',
        success: function(response) {
            console.log("SUCCESS")
            let item = JSON.parse(response);
            console.log(response)
            for ( i of item ) {
                console.log(i['fields']['image'])
                console.log(i['fields']['description'])
            $("#"+combo_category+"-image").html(`<img class="combo-img" src="/media/`+i['fields']['image']+`">`);
            $("#"+combo_category+"-description").html(i['fields']['description']);
            }
        },
        error: function(response){
            alert(response.error); 
        }
    });
}
