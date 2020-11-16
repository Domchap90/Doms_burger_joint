const { test } = QUnit;

QUnit.module('Menu filter tests:', function(hooks) {
    hooks.afterEach( function() {
        // Hook resets button state
        $('#price_asc').prop("checked", false);
        $('#price_desc').prop("checked", false);
    });

    test('getFilteredResults working', function(assert) {
        assert.expect(2);

        // Trigger function to be called with price ascending sort
        $('#price_asc').trigger('click');
        $('button[type="submit"]').trigger('click');

        // Awaits done() call before making assertions
        let done = assert.async();
        
        let expectedData = {
            'sort_key': 'price_asc',
            'category': 'burgers'
        }

        // Setup mock ajax response to intercept actual AJAX calls - avoids live server testing
        $.mockjax({
            url: "sort/",
            contentType: 'application/text',
            proxy: 'mock_data.txt'                
        });
        
        $.ajax({
            type: 'GET',
            url: "sort/",
            success: function(response) {
                // Same as in menu_filter.js 
                let counter = 0;
                for (item of JSON.parse(response)) {
                    counter++;
                    $("#item_name_" + counter).html(item['fields']['name']);
                    $("#item_pic_" + counter).attr('src', '/media/' + item['fields']['image']);
                    $("#item_desc_inline_" + counter).html(item['fields']['description']);
                    $("#item_price_" + counter).html(item['fields']['price']);
                    $("#item_desc_block_" + counter).html(item['fields']['description']);
                }
            }
        });

        setTimeout(function() {
            // Read prices from manipulated DOM
            let firstPriceListed = parseFloat($("#item_price_1").html());
            let secondPriceListed = parseFloat($("#item_price_2").html());
            let thirdPriceListed = parseFloat($("#item_price_3").html());

            // Data sent from ajax call is matching the data from filter buttons pressed
            assert.deepEqual($.mockjax.unmockedAjaxCalls()[0]['data'], expectedData, "correct data sent");

            // Items price sorted in ascending order
            assert.ok(thirdPriceListed > secondPriceListed && secondPriceListed > firstPriceListed, "list in ascending order");
            
            done();
        }, 2000)
    });

    QUnit.module('sortSwitchState', function(hooks) {
        hooks.afterEach( function() {
            $('#price_asc').prop("checked", false);
            $('#price_desc').prop("checked", false);
        });

        QUnit.test('toggles switch A on/off after click,', function(assert) {
            $('#price_desc').trigger('click');
            let switchA = $('#price_desc').is(':checked');
            let switchB = $('#price_asc').is(':checked');
            assert.propEqual(switchA, true, 'switch A is on');
            assert.propEqual(switchB, false, 'switch B stays off');
            $('#price_desc').trigger('click');
            assert.propEqual(switchA, false, 'after another click switch A is off');
        });

        QUnit.test('switch A is on, switch B is off: Upon clicking B ', function(assert) {
            $('#price_desc').trigger('click');
            $('#price_asc').trigger('click');
            let switchA = $('#price_desc').is(':checked');
            assert.propEqual(switchA, false, 'switch A turns off.');
            let switchB= $('#price_asc').is(':checked');
            assert.propEqual(switchB, true, 'switch B turns on.');
        });
    });
});
