$(document).ready(function() {
    $('.detail-order-row').hide();
    $('.general-order-row').click(function(){
    /* Creates accordian effect where only one row's details can be viewed at
    a time */
        let detailRowId = $(this).next().attr('id');

        // Allows the single viewed row to be closed so all rows are hidden
        $('.detail-order-row:not(#'+detailRowId+')').hide();
        $(this).next().toggle();
    });
    controlPaginationMenuLength();
});

// Change number of pagination buttons according to screen size
window.addEventListener('resize', controlPaginationMenuLength);

function controlPaginationMenuLength() {
    const paginatedNumberBtns = $('.pagination li:not(.arrow-btn)');
    paginatedNumberBtns.hide();
    const activeElement = parseInt($('.pagination .active').html());
    
    if ($(window).width () < 601) {
        // show 5 page buttons below 601px res
        displayButtons(paginatedNumberBtns, activeElement, 5);
        if (paginatedNumberBtns.length < 5) {
            $('.pagination').width("fit-content");
        }
    } else if ($(window).width () < 901) {
        displayButtons(paginatedNumberBtns, activeElement, 7);
        if (paginatedNumberBtns.length < 7) {
            $('.pagination').width("fit-content");
        }
    } else {
        displayButtons(paginatedNumberBtns, activeElement, 10);
        if (paginatedNumberBtns.length < 10) {
            $('.pagination').width("fit-content");
        }
    }
}

function displayButtons(
    paginatedNumberBtns, activeElement, numPageBtnsToDisplay) {
// Limits the number of paginated buttons to be displayed when there are many 
    
    let btnsToDisplay = [];
    /* limits will dictate the number of buttons either side of the active 
    element */
    const limit = numPageBtnsToDisplay/2;

    for (numberBtn of paginatedNumberBtns){
        // read page number from id of button
        let numberBtnValue = parseInt(numberBtn.id.split('_')[1]);
        if (activeElement > limit) {
        /* enforces limits when active element is greater than number of pages
        to be displayed / 2 */
            if(numberBtnValue <= (
               activeElement + limit) && numberBtnValue > (
                   activeElement - limit)) {
                btnsToDisplay.push(numberBtn);
            }
        } else {
        // otherwise show the first number of pages to be displayed as per input
            if(numberBtnValue < numPageBtnsToDisplay + 1) {
                btnsToDisplay.push(numberBtn);
            }
        }
    }
    for (btn of btnsToDisplay) {
        $(btn).show();
    }
}
