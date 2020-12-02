const { test } = QUnit;

QUnit.module('Accordian effect', function(hook){
    hook.afterEach(function(){
        // reset all detail-order-rows to hidden
        $('tbody tr:nth-child(even)').each(function() {
            $(this).hide();
        });
    });

    test('Initial state:', function(assert) {
        // Get initial state
        $(document).ready();
    
        $('.detail-order-row').each(function(i){
            i++;
            assert.ok($(this).is(":hidden"), `row ${i}'s contents are hidden`);
        });
    });

    test('Click row of table ', function(assert) {
        // Odd table rows are the clickable rows of the table
        $('tbody tr:nth-child(odd)').each(function(i) {
            i++;
            $(this).trigger('click');
            assert.ok($(this).next().is(":hidden")==false,
                     `row ${i}'s contents are now showing`);
        });
    });

    test('Click same row of table AGAIN ', function(assert) {
        $('tbody tr:nth-child(odd)').each(function(i) {
            i++;
            $(this).next().show();
            $(this).trigger('click');
            assert.ok($(this).next().is(":hidden"),
                      `row ${i}'s contents are back to their hidden state`);
        });
    });

    test("Click row of order table with another row's body open ",
         function(assert) {
        $('#detail_0123').show();
        $('tbody tr:nth-child(3)').trigger('click');

        assert.ok(
            $('#detail_0123').is(':hidden'),
            "row 1's body closes as row 2 is clicked");

        $('#detail_0234').show();
        $('tbody tr:nth-child(5)').trigger('click');

        assert.ok(
            $('#detail_0234').is(':hidden'),
            "row 2's body closes as row 3 is clicked");

        $('#detail_0345').show();
        $('tbody tr:nth-child(1)').trigger('click');

        assert.ok(
            $('#detail_0345').is(':hidden'),
            "row 3's body closes as row 1 is clicked");
    });
    
});
