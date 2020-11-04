$('.switch').find("input[type=checkbox]").on("click",function() {
    let switchID = $(this).parent().parent().attr('id');
    let switchOn = $('#'+switchID).find("input[type=checkbox]").is(':checked');
    let otherSwitchID;
    console.log(switchID+' turned on: '+switchOn)
    if (switchID==='price_low_high') {
        otherSwitchID='price_high_low';
    } else {
        otherSwitchID='price_low_high';
    }
    let otherSwitchOn = $('#'+otherSwitchID).find("input[type=checkbox]").is(':checked');

    if (otherSwitchOn){
        $('#'+otherSwitchID).find("input[type=checkbox]").prop("checked", false);
    }
});

function getFilteredResults(category_name) {
    let sort;
    if ($('#price_desc').is(':checked')) {
        sort='price_desc';
        console.log('desc is checked.')
    } else {
        sort='price_asc';
        console.log('asc is checked.')
    }
    let dataToSend = {
               'sort_key': sort,
               'category': category_name
            }
    console.log('sort='+sort+', category_name='+category_name)
    console.log('sort type='+typeof sort+', category_name type ='+typeof category_name)
    $.ajax({
        type: 'GET',
        url: "sort/",
        data: dataToSend,
        dataType: 'json',
        success: function(response) {
            let itemsList = JSON.parse(response['items']);
            let counter = 0;
            for(item of itemsList) {
                counter++;
                $("#item_name_"+counter).html(item['fields']['name']);
                $("#item_pic_"+counter).attr('src', '/media/'+item['fields']['image']);
                $("#item_desc_inline_"+counter).html(item['fields']['description']);
                $("#item_price_"+counter).html(item['fields']['price']);
                $("#item_desc_block_"+counter).html(item['fields']['description']);
                }
            }
        })
    }