// Adds listener event to filter switches
$('.switch').find("input[type=checkbox]").on("click",function() {
    let switchID = $(this).parent().parent().attr('id');
    let otherSwitchID;

    if (switchID==='price_low_high') {
        otherSwitchID='price_high_low';
    } else {
        otherSwitchID='price_low_high';
    }
    let otherSwitchOn = $(
        '#'+otherSwitchID).find("input[type=checkbox]").is(':checked');

    if (otherSwitchOn){
    // Prevents both switches being on at the same time.
        $('#'+otherSwitchID).find("input[type=checkbox]").prop(
            "checked", false);
    }
});

function getFilteredResults(category_name) {
    let sort;
    if ($('#price_desc').is(':checked')) {
        sort='price_desc';
    } else {
        sort='price_asc';
    }
    let dataToSend = {
        'sort_key': sort,
        'category': category_name
    }

    $.ajax({
        type: 'GET',
        url: "sort/",
        data: dataToSend,
        dataType: 'json',
        success: function(response) {
            console.log("SUCCESS");
            const itemsList = JSON.parse(response);
            let counter = 0;
            for(let item of itemsList) {
                counter++;
                $("#item_name_"+counter).html(item['fields']['name']);
                $("#item_pic_"+counter).attr(
                    'src', '/static/menu_images/'+item['fields']['image']);
                $("#item_desc_inline_"+counter).html(
                    item['fields']['description']);
                $("#item_price_"+counter).html(item['fields']['price']);
                $("#item_desc_block_"+counter).html(
                    item['fields']['description']);
            }
        }
    })
}
