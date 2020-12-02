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
        
        let expectedSortData = {
            'sort_key': 'price_asc',
            'category': 'burgers'
        }

        /* Setup mock ajax response to intercept actual AJAX calls - avoids
        live server testing */
        $.mockjax({
            url: "sort/",
            contentType: 'application/text',
            proxy: 'menu_mock_data/sort_mock_data.txt'                
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
                    $("#item_pic_" + counter).attr(
                        'src', '/static/menu_images/' + item['fields']['image']);
                    $("#item_desc_inline_" + counter).html(
                        item['fields']['description']);
                    $("#item_price_" + counter).html(
                        item['fields']['price']);
                    $("#item_desc_block_" + counter).html(
                        item['fields']['description']);
                }
            }
        });

        setTimeout(function() {
            // Read prices from manipulated DOM
            let firstPriceListed = parseFloat($("#item_price_1").html());
            let secondPriceListed = parseFloat($("#item_price_2").html());
            let thirdPriceListed = parseFloat($("#item_price_3").html());

            /* Data sent from ajax call is matching the data from filter
            buttons pressed */
            assert.deepEqual($.mockjax.unmockedAjaxCalls()[0]['data'],
                             expectedSortData, "correct data sent");

            // Items price sorted in ascending order
            assert.ok(thirdPriceListed > secondPriceListed && 
                      secondPriceListed > firstPriceListed,
                      "list in ascending order");

            $.mockjax.clear();
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
            assert.propEqual(
                switchA, false, 'after another click switch A is off');
        });

        QUnit.test('switch A is on, switch B is off: Upon clicking B ',
                   function(assert) {
            $('#price_desc').trigger('click');
            $('#price_asc').trigger('click');
            let switchA = $('#price_desc').is(':checked');
            assert.propEqual(switchA, false, 'switch A turns off.');
            let switchB= $('#price_asc').is(':checked');
            assert.propEqual(switchB, true, 'switch B turns on.');
        });
    });
});

QUnit.module('Combo items tests:', function(hooks) {
    hooks.afterEach( function () {
        $('#c3_starter').val('');
        $('#c3_main').val('');
        $('#c3_dessert').val('');
        $('#c3_drink').val('');
        $("#c3_starter_image").empty();
        $("#c3_starter_description").empty();
    })

    test('validateComboForm working', function(assert) {
        assert.expect(5);
        $('#c3_starter').val('soup');
        $('#c3_main').val('chicken');
        $('#c3_dessert').val('doughnut');
        $('#c3_drink').val('cola');
        $('.form-error').attr('id','err_3');

        $('#combo_btn').trigger('click');
        assert.ok($('.form-error#err_3').is(':empty'),
                 'no errors rendered when form is complete');
        let formInputs = $('form').children('input');

        for (input of formInputs){
            // Fill all inputs in
            for (inputInner of formInputs){
                $(inputInner).val('rice');
            }
            // Except for one
            $(input).val('');

            $('#combo_btn').trigger('click');
            /* Check error message is raised when form is submitted with
            empty field. */
            assert.equal(
                $('.form-error#err_3').html(),
                `<p>Please select all food options to add the combo to your \
order.</p>`,
                "error message displaying for empty "+input.name+" field");
        }
    });

    test('updateComboSelection working', function(assert) {
        assert.expect(3);
        let done = assert.async();

        // Set value to update info for
        $('#c3_starter').val('whitebait');
        $('#c3_starter').trigger('change');
        let selectedVal = $('#c3_starter').val();
        let combo_category = $('#c3_starter').attr('id');
        let expectedItemData = {'food_id': selectedVal}
        // Initialize array to collect response items
        let responseItems = []

        $.mockjax({
            url: 'item/',
            dataType: 'json',
            proxy: 'menu_mock_data/combo_mock_data.txt', 
        });

        $.ajax({
            type: 'GET',
            url: 'item/',
            success: function(response) {
                let item = JSON.parse(response);  
                for ( i of item ) { 
                    $("#"+combo_category+"_image").html(
                        `<img class="combo-img" src="/static/menu_images/`+
                        i['fields']['image']+`">`);
                    $("#"+combo_category+"_description").html(
                        i['fields']['description']);

                    // Collect results for assertion
                    responseItems.push("/static/menu_images/"+i['fields']['image'],
                                       i['fields']['description'])
                }
            },
            error: function(response){
                alert(response.error); 
            }
        });

        setTimeout(function() {
            /* Get updated field information from DOM to compare against the
            ajax response info */
            let changedFieldImgSrc = $("#c3_starter_image img").attr('src'); 
            let changedFieldDesc = $("#c3_starter_description").html();

            // Data sent from ajax call is matching the item changed in form
            assert.deepEqual(
                $.mockjax.unmockedAjaxCalls()[0]['data'],
                expectedItemData, "correct data sent"
                );

            // ajax response correctly updates changed fields information
            assert.equal(responseItems[0], changedFieldImgSrc,
                         "image updated correctly");
            assert.equal(
                responseItems[1], changedFieldDesc,
                "description updated correctly");

            $.mockjax.clear();
            done();
        }, 2000)

    });
});
