$(document).ready(function(){
    $('select').formSelect();
    $('.collapsible').collapsible();
});

function validateComboForm(form) {
    /* Notifies user that all form fields have to be selected in order to send
    the form. */

    $('.form-error#err_'+form).empty();
    const addComboForm = document.forms["add_combo_"+form];

    for (let field of addComboForm) {
        if ($(field).prop('required') && field.value=='') {
            $('.form-error#err_'+form).html(`<p>Please select all food options \
to add the combo to your order.</p>`);
        }
    }
}

function updateComboSelection(selectedItem){
    /* From changed field id, function sends ajax call to server and 
    dynamically updates item's info on page (image and description) */
    let selectedID = selectedItem.value;
    let combo_category = selectedItem.id;
    let itemData = {
        'food_id': selectedID
    }

    $.ajax({
        type: 'GET',
        url: 'item/',
        data: itemData,
        dataType: 'json',
        success: function(response) {
            let item = JSON.parse(response);

            for (let i of item ) {
                $("#"+combo_category+"_image").html(
                    `<img class="combo-img" src="/static/menu_images/`+
                    i['fields']['image']+`">`);
                $("#"+combo_category+"_description").html(
                    i['fields']['description']);
            }
        },
        error: function(response){
            alert(response.error); 
        }
    });
}
