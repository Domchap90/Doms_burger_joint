# Dom's Burger Joint 

A prototype for a burger delivery service's web application. Serving customers within the local region of central London.

# Contents

1. UX Design
    - [Site Goals](#site-goals)
    - [User Goals](#user-goals)
    - [User Stories](#user-stories)
    - [Color scheme](#color-scheme)
    - [Wireframes](#wireframes)

2. Features
    - [Core Features](#core-features)
    - [Non Essential Features](#non-essential-features)
    - [Features Left to Implement](#features-left-to-implement)

3. Technologies Used
    
4. Testing
    - [Automated Testing](#automated-testing)
    - [Manual Testing](#manual-testing)

5. Deployment

6. Credits
    - [Content](#content)
    - [Media](#media)
    - [Code](#code)
    - [Acknowledgements](#acknowledgements)

# UX Design
## Site Goals

- Attract customers through all areas of the site.
- Create excitement that eventually leads to an online sale.
- Make it easy for customers to purchase food online.
- Upsell other food items that the customer may have not initially considered to purchase.
- Encourage users who haven't visited the site before to sign up to the members area.
- Create service that rewards member loyalty.
- Handle user's information securely.

## User Goals
- Wants the site to look professional as this will most likely reflect the food quality.
- Easily navigate the site and find whatever they need within 3 clicks.
- Have plenty of information about what they are going to order to help them decide.
- Have some way of adjusting their order, if they need to change the quantity or remove an item.
- Be able to save money if ordering as a group.
- Have vegetarian options.
- Receive confirmation after their order has been placed via email.
- If they are a regular user they will want to be able to save money via a loyalty scheme.

## User Stories


| Story ID | As a | I want to be able to... | So that i can... |
| ----------- | ----------- | ----------- | ----------- |
| 1 | Customer | View food and drink products |	See what i want to order |
| 2	| Customer | Add food/ drink to checkout | Review my order before paying |
| 3 | Customer | Search for food items based on allergens | Find suitable food for me |
| 4 | Customer | Search for food items based on vegetarian | Find suitable food for me |
| 5 | Customer | Search for food items based on Popularity & Price | Make a decision more easily |
| 6 | Customer | Have the option of ordering my food to collect | Get it on the way home/ still make an order if i live too far away |
| 7 | Customer | Be able to find out if i'm eligible for delivery before i make an order | Save time / convenience |
| Checkout |			
| 8 | Customer | View my checkout at any time from any page on site | Make my order quickly |
| 9 | Customer | Change food/drink item in checkout | Change my mind and order something else |
| 10 | Customer | Change food/drink item size in checkout |	Change my mind and order bigger/smaller |
| 11 | Customer | Change food/drink item quantity in checkout |	Change my mind and order more/less |
| 12 | Customer	| Confirm my order before proceeding to checkout | Check everything is correct before paying |
| Payment |
| 13 | Customer | Pay for something quickly with little hassle | Complete order quickly |
| 14 | Customer | Pay securely and have confirmation of my payment sent to me via email. | Have proof of payment if order doesn't come through or is incorrect |
| 15 | Customer	| Confirm my payment before taking the money out | Acknowledge correct details and amount of spending |
| 16 | Customer	| Have my payment on record even if my computer crashes during submitting payment | Still have my food delivered to me |
| Site Admin |
| 17 | Site Manager | Perform CRUD operations on food and drinks items from menu | Update the menu when it changes |
| 18 | Site Manager | Update prices of food and drinks items | Keep the website prices consistent with what people pay inside restaurant |
| User profile	|		
| 19 | Site user | Update my Billing/ Shipping Address | Receive the deliveries to the correct address |
| 20 | Site user | View my order history at Dom's Burger Joint | Check my orders - what i've eaten & how much i've spent |
| 21 | Site user | Make same order as I have in the past | Create order more quickly and eat my regular preference of food |


## Color scheme

- Predominant background color: white
- Other background colors used: #ededed, #d4d4d4 & #fafafa
- Header and paragraph text color: black
- Buttons: background - black, foreground text - white
hover: background - yellow, foreground text - black

## Wireframes

### Home page
<img src="static/wireframes/home.png" alt="markup of home page">

### Menu page
<img src="static/wireframes/menu.png" alt="markup of menu page">

### Combo Deals page
<img src="static/wireframes/combos.png" alt="markup of combo deals page">

### Order page
<img src="static/wireframes/orders.png" alt="markup of order page">

### Member's Promo page
<img src="static/wireframes/members_promo.png" alt="markup of member's promo page">

### Member's Area page
<img src="static/wireframes/members_area.png" alt="markup of member's area page">

### Checkout page
<img src="static/wireframes/checkout.png" alt="markup of checkout page">

### Checkout Success page
<img src="static/wireframes/checkout_success.png" alt="markup of checkout success page">

### Login page
<img src="static/wireframes/login.png" alt="markup of login page">



# Features
## Core Features

- As the user will have to pay for their burgers & the company that runs the website need to get paid, a payment feature is essential.
User stories 13 & 15 will be incorporated by integrating Stripe payment system. 14 & 16 will be considered very much standard practice with online payments
and these features will be implemented using webhooks. In the event that the user somehow makes an error during checkout and their computer crashes after clicking the submit button.
The payment will still go through and the webhook will allow a confirmation email to be sent to the user through the webhook handler in the app.

- The confirmation process will take place once the user has selected all their items to purchase then 2 further pages will have to be visited. 
The first being where the user decides whether or not they want their order delivered to them or to be collected at the store (user story 6). 
The second will be where the details of the payment must be made and any relevant delivery or contact information. Since picking their items, the user will have had to make
3 clicks in total to submit their order. Therefore ommitting the need for a modal to appear at checkout submission as this would be overkill & potentially frustrate the customer.

- The user is constantly reminded of how much they are going to spend by the grand total being written in the proceed to checkout button, the place order button as well as in the actual order table itself.
So there is no sense of the user being tricked into paying for something or there is very little risk of accidentally purchasing food that they didn't mean to.

- Another essential feature is ofcourse the potential customer being able to add food and drinks items to their order. For this to happen, 
the food items must be viewable and it must be clear and intuitive how to navigate to these items. The foods will be grouped as a typical menu would be -
by course. In the nav bar link aptly named "menu" which will contain a drop down menu of the categories as seen in the wireframe for home page.

- Foods will be added via simple forms that consist of select input boxes & an 'add' button for each item. This will post a form to the backend and
accumulatively build an order that is available via the django context session variable meaning it can be accessed from any app. The food order will be needed
in the menu where it is built, the order app where it is edited and the checkout where it is saved and submitted.

User stories: 1, 2, 8, 9, 10, 11, 12, 13, 14, 15, 16

## Non Essential Features

With vegetarianism being very popular these days and 'vege' burgers becoming a big trend in their own right, a small subsection of burgers will be filtered through 
the menu options as vegetarian (User Story 4). This will be treated as a separate category and then joined with the burger category in searches for combos etc.

The menu will have a price filter at the top right hand corner of the page below the nav bar for the more price conscious customers. Allowing the user to
present the menu items from low to high price or vice versa. Similarly this is done with popularity of the food items ordered, although no switch is available on 
this filtering option because why would customers want to see the least popular items? The popular page shows 3 of the most ordered burgers, 1 of each for the most
ordered side, dessert & drink (User Story 5).

Unlike delivering from an ecommerce store where essentially no where is off limits. With food delivery, the food has to be served fresh and hot, therefore the distance the user is 
from the store has to be taken into account. Not all visitors to the site will be eligible for delivery and therefore it is nice to have another option. If the customer is willing
to travel to the store they can collect. This doesn't really affect the checkout process too much other than the order model must state whether it is for collection or delivery & 
must collect the appropriate information for each type. The collection fields on the checkout form will be the same barr fields pertaining to delivery - address lines and postcode
(User Story 6).

It would be rather unpleasant for the user who wanted an order for delivery to have to pick everything they wanted and fill out most of their details only to find out they are not eligible
for delivery. Hence user story 7 that allows the user to see their eligibility immediately from the home page.

User story 19 is really for repeat customers. On the member's customized page they have the option to save their details of things like address and contact information to avoid having to enter
this every single time that they want to checkout an order. This saves time and increases likelihood of them making another order with DBJ.

If a user wants to see what they've ordered in the past or can't remember how much they spent on an order then they can view all these little details in tabular form in their profile page.
Better still if they want to repeat another order again being a creature of habit they have this option. This saves time by bypassing building an order from no items. Jumping straight to
only having to enter their card details. For security reasons this cannot be saved (User Story 20 & 21).
 

User stories: 4, 5, 6, 7, 19, 20, 21

## Features Left to Implement

Due to time restrictions not all features will be implemented. From a health and safety perspective if the website were to go live for a real business delivering
food to paying customers then of course allergens would have to be considered. At the very minimum they would have to be listed in each of the food options. However 
as this is a hobby/ educational project and not commercial the legislative principles can be ignored. Furthermore to filter the menu options based on which allergens
they contain may be useful to some users who suffer from allergies but even then the mere listing of whether those allergens are present would be enough. Most customers
wouldn't search for what they wanted to eat based on this (User Story 3).

Whilst there is currently no customized format for a site manager to edit, add or delete food items. All of these actions can be performed in the Django admin interface
by the super user. This could be added in after a few months of usage when the site owner wants to change the menu (User Stories 17, 18).

User stories: 3, 17, 18

# Technologies Used

# Testing
## Automated Testing
### HTML Validation
#### Running Tests

- Each html template was copied into the W3C validation service (https://validator.w3.org/#validate_by_input) and the 'check' button clicked.
- Each error/ warning assessed and if independent of django template framework the error was corrected.
- Only files which were amended by myself were tested, leaving many of the allauth files untested.
- Tested 11 templates in this manner including the 'base.html'.

#### Results

Only reporting non Django template related errors, the main issue flagged was the repeated use of either buttons as descendants of anchor tags
or vice versa. After this was flagged in one of the initial tests, the button class was created in 'base.css' (lines 69-78) to allow links to look
exactly the same and behave almost identically to an actual button element. All the html was amended to modify any combination of buttons and anchor
tags to anchor tags alone holding the class 'button'. Any ids or classes the button tag had were passed onto the anchor tag. After doing this the
button/ link functionality was retested.

Buttons were still left in the code only for form submissions however.

Small issues were flagged such as the occasional missing '/' at the start of a closing tag. These were easily fixed on the spot.

Eventually tests were run until no more significant errors/warnings were flagged.

### CSS Validation
#### Running Tests

- Each css file was copied into the W3C validation service (https://jigsaw.w3.org/css-validator/#validate_by_input) and the 'check' button clicked.
- Six css files were tested in total: 'base.css' plus the css file from every app.

#### Results

<p>
    <a href="http://jigsaw.w3.org/css-validator/check/referer">
        <img style="border:0;width:88px;height:31px"
            src="http://jigsaw.w3.org/css-validator/images/vcss"
            alt="Valid CSS!" />
    </a>
</p>
All tests passed with no errors or significant warnings. There were some minor warnings about using same 'border-color' as 'background-color'. 
However this was done in anticipation of the hover effect changing the background-color to reveal the contrasting border color.

### Django Testing (Python code)
#### Running Tests

- Prior to running any tests, in the settings page of the core app comment out lines 113 - 117 & remove indentation for DATABASES object underneath.
Also comment out line 173 as instructed.

- To run one specific python test file, enter in CLI:<br>
    python3 manage.py test [app_name].[test_file]

- If not installed already, enter in CLI: <br>
    pip3 install coverage

- To run python tests for an entire app, enter in CLI:<br>
    coverage run --source=[app_name] manage.py test

- '.' signifies a pass, while 'F' signifies a fail & 'E' signifies an error.

- See what percentage of the app's code has been tested by entering in CLI:<br>
    coverage report

- To examine this in more detail and view exactly which lines of code have been tested:
  - (CLI command) coverage html
  - (CLI command) python3 -m http.server
  - Open browser by ctrl + click on http link and selecting htmlcov/
  - select file to be viewed.

** Note coverage report only reveals what % is tested NOT passed

#### Results

##### Checkout

- forms.py 5 tests ran: all passed
- models.py 7 tests ran: all passed
- signals.py 4 tests ran: all passed
- views.py 18 tests ran: all passed
- coverage report 86%

All the files were extensively tested although 86% isn't considered high, ideally this would be 100%. However
the webhooks were tested manually and this accounts for most of the remainder.

##### Food Order

- views.py 7 tests ran: all passed
- coverage report 99%

Despite only having one test file for this app it still managed to cover almost all python lines of code.

##### Home

- views.py 3 tests ran: all passed
- coverage report 94%

The missing lines of code from the tests were the exceptions blocks in case of the Google Maps API call failing.
Whilst mock API responses could have been used in automated testing to replicate this. Instead manual testing was
chosen to get authentic fails from the API.

##### Members Area

- forms.py 4 tests ran: all passed
- models.py 3 tests ran: all passed
- views.py 3 tests ran: all passed
- coverage report 99%

##### Menu

- models.py 3 tests ran: all passed
- views.py 6 tests ran: all passed
- coverage report 98%

### Qunit Testing (Javascript) 
#### Running Tests

- To run the automated js tests simply type into CLI: python3 -m http.server
- (CLI command) python3 -m http.server
- Open browser by ctrl + click on http link and selecting 'js_tests/'
- Select test to be run. This will be a file of type '.html'.
** Note: Many of the tests have async components due to Ajax calls being made within functions.
This may cause a slight delay in rendering the results.

#### Results
##### Checkout

This wasn't heavily tested automatically due to the two AJAX calls within the 'stripe_element.js' file.
Meaning it was very much integrated with the back end and therefore most of the logic testing was completed
in the django view instead. Here the goal was primarily to ensure that the correct AJAX calls were sent from the 
javascript functions by intercepting the calls via mockjax and using assert equals statements to find the urls
and data sent from the calls was indeed correct.

The spending warning button state was completely tested. There is the possibility of the user reaching the checkout page
by entering the checkout url despite the assumption of the 'proceed to checkout' button being successfully disabled
on the food order page. It's important that the system doesn't allow invalid orders to be made as this could potentially
lead to a messy job of distinguishing valid orders from non valid in the admin page. Plus the user won't want to spend 
the delivery fee for nothing.

All tests passed. 

##### Food Order

The 'quantity_buttons.js' file was extensively tested as this is a key piece of javascript for dynamically altering
the order page. The importance of this cannot be stressed enough because if the user for example increases the quantity of an item
& the javascript does not update the totals correctly. This could potentially result in the user getting free food but more importantly
the business losing money.

The structure of the code is a long chain of functions to control isolated aspects of the buttons, such as assessing their states 
(disabled or not), updating their states & calls to backend to evaluate these aspects. If there is one function that doesn't perform
as expected then the whole chain breaks down and the system is flawed. Here lies the reason why these tests were more integration based
rather than unit tested. Unit testing could have been increased further by all means but due to the chaining nature of the functions,
the tests were structured around triggering an event (namely clicks of a button) and yielding an expected result through DOM manipulation.

The financial gravity of mistakes in this section is a key reason why it was tested manually as well.

All tests passed. 

##### Home

No JS to test.

##### Members Area

The javascript's role in this app was purely to control the display of the order history table for the logged in user in 2
ways:
1. To enforce an accordian effect with the table's header and body rows.
2. To control the number of paginated buttons on display for the table (varying according to screen size).

1. The 'tests.js' static file in the 'members_area' app focused on testing this.
2. Due to the responsive nature of this test, it would be very difficult to execute using Qunit. Therefore manual testing
was applied. 

All tests passed. 

##### Menu

The 'menu' app has two js files to test.  

- menu_filter.js
  1. Toggles switches appropriately so that 2 switches are never 'on' at the same instant.
  2. Applies filtering as dictated by the switch state via an Ajax call to the sort items view.
- combo_items.js
  1. Validates form, essentially highlighting any missing fields from the combo.
  2. Dynamically updates chosen food item content such as description and image.

These are pretty straight forward DOM manipulation tests. The benefit of using Qunit was to create a test DOM where any number
of tests and manipulations could be carried out and assessed almost instantly. Which saves time with regards to future adjustments 
& testing. 

No manual testing required here.

All tests passed.

## Manual Testing
### Checkout Form Validation
#### Submits valid data

Proceed through checkout as a customer would do. Entering details that should pass form validation and be redirected to the checkout success
page. 

    Valid data to submit 
        Name = James
        Mobile = 07777 555 555
        Email = test@domain.co.uk
        Address Line 1 = 101 random st
        Address Line 2 = random town
        Post Code = W1W 7JB
        Delivery instructions = (leave blank)
        Payment = 4242424242424242 04/24 242 (Test payment data)
    

1. Ensure order has a valid total amount by selecting enough items in the menu.
2. Proceed through orders and click 'Delivery' button.
3. Fill out checkout form with valid data to submit.
4. Click 'Place your order' button to submit the form.
5. Observe:
    1. Next page loaded
    2. Details rendered on page.

Expected outcome should render:

1. checkout success page.
2. The following observations:
    - Order number matches the last parameter of the url.
    - Order details matched the initial chosen items from the menu.
    - 'Sent to' section should contain the address fields as entered in test.
    - 'Your details' section should contain the personal details as entered in the test 
  
Test passed.

#### Rejects invalid data

Proceed through checkout as a customer would do. However enter details that should not pass form validation and dynamically highlight errors
within the checkout form.

    Invalid data to submit 
        Name = (leave blank)
        Mobile = 07777 555 555 22 (too long)
        Email = testdomain.co.uk  (no '@' char)
        Address Line 1 = 101 random st
        Address Line 2 = random town
        Post Code = W1W 7J
        Delivery Instructions = (leave blank)
        Payment = 5555555555555555 12/12 121

1. Repeat steps 1 - 5 for 'Submits valid data' test, however this time enter the invalid data to submit instead.

Expected outcome should render:

1. Checkout form page after loading visual dissappears.
2. The following errors:
    - Name error - "This field is required."
    - Mobile error - "This phone number is too long. It can only have a maximum of 11 digits without a '+'."
    - Email error - "Enter a valid email address."
    - Postcode error - "Sorry it looks like you are not eligible for delivery. However please feel free to make an order for **collection**."
    - Payment error 'Your card number is invalid'.
      
Test passed.

### Reward Status 

With the customers reward status being known prior to starting the tests, it should correctly progress as each successful order is made. Reaching
a maximum of 5 - qualifying amount & a minimum of 0 - after using discount.

#### Correctly increases

1. Navigate to the admin page by using the base url + '/admin/'.
2. Under 'Authentication and Authorization' select 'users', then click on the user's username to see their details.
3. Set their reward status to 4.
4. Login as that user.
5. In the user's profile page *Note* the number of golden burger icons.
6. Fill order with items to total over the minimum delivery amount, proceed to checkout, delivery.
7. Fill out form with valid details and submit.
8. *Note* if discount applied in checkout success page.
9. Upon reaching checkout success page, navigate to members area whilst staying logged in.
10. *Note* the number of golden burger icons out of 5.

Expected outcome is:

5. 4
8. No discount applied
10. 5

Test passed.

#### Correctly resets

Following on from the 'Correctly increases' test:

1. Staying logged in as the same user as the previous test, now repeat stages 5 - 10.

Expected outcome is:
5. 5
8. Discount applied
10. 0

Test passed.

### Webhooks 

Webhooks are the most intricate system being used in the entire app. Therefore it's worth doing thorough testing 
to ensure that the app is communicating properly with Stripe. Webhooks are responsible for sending data back to the app's server
not too disimilar from an API. In Stripe's case it is authorizing & processing payment data that has been sent to stripe with a
payment intent object.

Stripe tells the server whether the charge has succeeded & other various pieces of information about what stage of completion 
the payment intent has reached for development purposes. These are accessible from the Stripe dashboard 
(https://dashboard.stripe.com/test/webhooks).

In this app's checkout system Stripe's webhooks also serve as a fallback for the user not reaching the checkout success page for whatever reason.
Perhaps they accidentally close the window after clicking submit. In this case, the user would be unsure of whether or not their order had been
processed by the business. For this situation some sort of feedback would be incredibly useful. Driving the decision to send an email via the
webhook handler. This email's contents vary depending on many factors:

1. The order type that was made - Collection or Delivery.
2. User logged in or not.
3. The reward status if the user was logged in.
4. Address information on the submitted checkout form.

The tests must cover all of these variables. Furthermore the webhooks not only serve as a fall back but they are the only means by which Stripe can 
communicate successful events directly to the server once they have occured at the Stripe end. Therefore they will have to be tested with the checkout success page 
being reached as well. 

When the webhooks are acting as a fallback, they assume the responsibility of creating the order and saving that information to the database. As well as altering
the reward status for the member. Upon the successful rendering of the checkout success page, the tests need to ensure that there has been no duplication of efforts
in the hand over of this responsibility. Specifically this means that two emails aren't sent to the user and they don't have two duplicate orders made at the same time.

#### Anonymous User Delivery

1. Ensure that any user profile is currently logged out.
2. Comment out line 191 in stripe_element.js to prevent form submitting.
3. Fill order with items to total over the minimum delivery amount, proceed to checkout via **Delivery** option.
4. Fill out form with [valid details](#submits-valid-data) and submit.
5. *Note* time & observe visual of page.
6. Navigate to django admin page for site & within the section checkout, orders.
7. Ensure orders are in the order of most recent at the top, then click on the top order.
8. *Note* is that the order recently made?
9. Navigate to your stripe dashboard.
10. *Note* stripe webhook events for the time noted in stage 5.
11. Check Terminal (if running from local IDE) for backend email details matching the users
information and order information. If running in heroku Check the user's email account for an email
from d0mch4pl3@gmail.com.
12. Undo stage 2 & repeat the test stages 3 - 11.

Expected outcome:

5. Page loading animation frozen.
8. True.
10. Stripe webhooks all succeed:
  - payment_intent.succeeded 
  - payment_intent.created
  - charge.succeeded
11. Email Details:
  - 'To' field of email reads 'test@domain.co.uk'
  - Identifies 'James' as recipient.
  - Correct date & time order was placed.
  - Sent to:
    - 101 random st
    - random town
    - W1W 7JB
  - Amount paid shows correct totals.

12. Expected outcome 5 will be different as the page loading animation no longer freezes but runs for a breif 
period of time before the checkout success page is rendered. The remaining outcomes 8, 10, 11 should be exactly 
the same with no duplicate emails or orders.

Anonymous user delivery test passed.

#### Member Delivery

1. Ensure that a member profile is currently logged in.
2. Set reward status to 4 in the admin page for the logged in member profile.
3. Comment out line 191 in stripe_element.js to prevent form submitting.
4. Fill order with items to total over the minimum online spend amount, proceed to checkout via **Delivery** option.
5. Fill out form with [valid details](#submits-valid-data) and submit.
6. *Note* time & observe visual of page.
7. Navigate to member's profile page & within the section 'Order History', open the top order.
8. *Note* is that the order recently made?
9. Navigate to your stripe dashboard.
10. *Note* stripe webhook events for the time noted in stage 6.
11. Check Terminal (if running from local IDE) for backend email details matching the users
information and order information. If running in heroku Check the user's email account for an email
from d0mch4pl3@gmail.com.
12. Repeat stages 4 - 11 two more times & *Note* the email message regarding reward status on each occasion
at stage 11.
13. Undo stage 3 & repeat the test stages 3 - 11 one more time ensuring no duplications.

Expected outcome:

6. Page loading animation frozen.
8. True.
10. Stripe webhooks all succeed:
  - payment_intent.succeeded 
  - payment_intent.created
  - charge.succeeded
11. Email Details:
  - 'To' field of email reads 'test@domain.co.uk'
  - Identifies 'James' as recipient.
  - Correct date & time order was placed.
  - Reward status messages: 
    - Reward status = 5

            Email message = "Almost there, you will receive a free burger on your next order."
    - (stage 12) Reward status = 0

            Email message = "Congratulations, you earned a free burger on this order."
    - (stage 12) Reward status = 1

            Email message = "Just 4 more order(s) needed to grab your free burger."
  - Sent to:
    - 101 random st
    - random town
    - W1W 7JB
  - Amount paid shows correct totals.

13. Expected outcome 6 will be different as the page loading animation no longer freezes but runs for a breif 
period of time before the checkout success page is rendered. The remaining outcomes 8, 10 should be 
the same with no duplicate emails or orders however 11 only includes one email result corresponding to a 
reward status of 2.

Member delivery test passed.

#### Collection Webhook Tests

Repeat this format of testing for 'Anonymous User Collection' & 'Member Collection' only changing the checkout method
to collect instead of delivery.

The expected outcomes for the collection tests are essentially the same apart from the email contents. Instead of
containing 'Sent to' address, the email will state the following:

    Available for collection from:
            20 Wardour St, 
            West End,
            London,
            W1D 6QG

All webhook collection tests passed.

### Quantity Buttons (Food order)

#### Test 1 Description

This test attempts to emulate a typical process a user may go through to select how many combos they want. The purpose here
is to ensure that any combination of combo packages that share the same type (e.g. family deal) can be selected as long as
their total quantity doesn't go over the combo sum limits as outlined in the quantity_buttons.js global variables (lines 18-21).

Combo items 1 & 3 have a combo sum limit of 5.

1. Ensure order is initially empty.
2. Navigate to 'DEALS', then 'COMBOS' via the nav bar.
3. Add two 'Regular Meal's or two 'Deluxe Meal's each containing different items.
4. Navigate to 'YOUR ORDER(2)' via the nav bar and *Note* the initial quantity button states.
5. Click on '+' quantity button for one of the combos until the button becomes disabled.
6. *Note* the quantity in the input box upon the button becoming disabled.
7. Now Click on the '-' quantity button for the same combo until the button becomes disabled.
8. *Note* the new quantity in the input box upon the '-' button becoming disabled.
9. Repeat stages 5 - 8 for the other combo

After completing the test, there should be 5 *Notes*. Each referring to the two numbers showing inside the two quantity inputs. Due to the 
combo sum quantity limits being equal to 5 for these two combos.
The expected output should render:<br>
(1, 1), (4, 1), (1, 1), (1, 4), (1, 1) 

#### Result 1

(1, 1), (4, 1), (1, 1), (1, 4), (1, 1) 

Test passed.

#### Test 2 Description

Another very similar test was conducted only on this occasion the limits were explored starting with quantity values initiated to 1 & 1 for combos
A & B respectively (initiated at step 4). However this time the combo is the 'Family Deal' (combo 2, combo sum limit 3).

4. Initiated Combo A: 1, Combo B: 1
5. Click on '+' quantity button for combo A until the button becomes disabled.
6. *Note* the quantity in the input box upon the button becoming disabled.
7. Now Click on the '-' quantity button for combo A until it becomes disabled.
8. *Note* the new quantity after the '-' button becomes disabled with A.
9. Repeat stages 5 - 8 for combo B.

After completing the test, there should be 5 *Notes*. Each referring to the two numbers showing inside the two quantity inputs.
The expected output should render:<br>
(1, 1) - A & B minus buttons disabled, (2, 1) - A plus button disabled & B minus disabled, (1, 1) - A & B minus buttons disabled, (1, 2) - A minus button disabled, B plus disabled, (1, 1) - A & B minus buttons disabled

#### Issue

Actual outcome:<br>
(1, 1), (2, 1), (2, 1), (2, 1), (2, 1)<br>

Upon performing the test, the disabled states were not being re-enabled after moving away from limits in certain cases.<br>

This bug was frustrating because no errors flagged it was a case of observing the buttons simply not change as they were expected to.

#### Solution: 

Console log statements were inserted into every conditional block of logic throughout the changeBtnState function to pick up which 
parts of my code were getting executed. Test 2 was then repeated with chrome developer tools open in the console view to observe the
output. <br>
It quickly became apparent that the final else block was never executed. Therefore the error lay within how the conditional statements
were structured . I had a long chained conditional sequence only allowing one block to be executed thereby if an add or minus button 
were to be disabled (at the limit), this was at the top of the chain of conditions. This wouldn't allow the opposite button to be re-enabled.

This problem tends to be specific with combos due to the summing nature of the limits allowing an upper limit and a lower limit to be closer
to each other on a particular combo.

Logic changed from:

    if(handling upper limit) {
        // disable plus button
    } else if(handling lower limit){
        // disable minus button
    } else (handling inbetween limits) {
        // re-enable both button states
    }

To:

    if(handing upper limit) {
    // disable plus button
    }else (handling not upper limit) {
        // re-enable plus button
    }

    if (handling lower limit){
        // disable minus button
    }
    else (handling not lower limit) {
        // re-enable minus button
    }

This logic doesn't assume that limits can't be only 1 quantity apart.

After this solution, the test was performed again and passed.

#### Test 3 Description

The primary goal of test 3 is to check that the state of the 'proceed to checkout' button is dynamically altered correctly depending on the total 
amount of the order.

1. In menu page of app, select any food item under £15.00. Then proceed to the order page.
2. Upon loading *note* the initial state of the proceed to checkout button, both visually & if the link is working.
3. Increase the quantity of the item you selected by clicking the add button until the total amount is over the minimum online threshold of £15.
4. The moment the threshold is passed, *note* the spending warning presence and state of 'Proceed to Checkout' button.
5. Reload the page.
6. repeat stage 2.
7. Decrease the quantity of the item you selected by clicking the minus button until the total amount is below the online threshold of £15.
8. Repeat stage 4.

After completing the test the expected *notes* should be as follows:<br>
2. Checkout button visually and functionally disabled with spending warning present.
4. Spending warning dissappears, checkout button becomes active. Totals increase.
6. No spending warning, checkout button active.
8. Spending warning appears, checkout button disabled.

#### Issue

Failed at stage 4. Checkout button was visually active (no disabled class) however upon clicking the link, nothing happened.

#### Solution

The corresponding link for the button was conditionally set to render via the django templates depending on if the backend value of remaining 
delivery amount was meeting a certain condition. Then javascript would disable or enable the button once a plus or minus quantity button was 
clicked triggering the long chain of methods that leads to the updateRemainingSpend function.

This worked fine if the intial page was rendered with the link however if it was rendered without and the user increases their spend via the 
qty buttons the 'updateRemainingSpend' function tries to enable a button that has no link attached to it.

To overcome this problem the initial responsibility of determining whether the button should be disabled was redelegated from the back end 
view to the front end, adding this as part of the doc ready function updateCheckoutBtnState() (lines 26 & 29 added). The link itself simply 
remained the same but no longer wrapped in the django conditional tags.

After implementing solution, the test was re-run and everything functioned properly.

### Google API Fail

In the function 'is_postcode_valid' line 34 of the home views file, the function contains an algorithm that checks whether or not the postcode is valid
in a number of ways. The parts which assess the string format of the postcode are tested automatically. The more intricate validation occurs through
the Google Maps API. Two calls are made to the API:<br>

1. Geocode call sends the string postcode to the API along with the key and returns the longitude, latitude coordinates.
2. Distance call sends the geocoordinates of two locations (store and user's address) and returns the distance between them.

All successful API call outcomes are tested automatically. In this section the instances where they fail will be tested manually to ensure that the app
doesn't crash and still yields a message to the user notifying them that their postcode isn't valid.

#### Test 1 Description

1. Line 62 in home app views file comment out "+settings.GOOGLEMAPS_API_KEY" and save the changes to file.
2. In terminal command line:<br>
    python3 manage.py runserver
3. Then open port in browser and type in a valid postcode such as "W1W 7JE" & press 'Check Delivery Eligibility' button.
4. Observe message output below button.
5. Undo the comment made in stage 1 to reset view back to original state.

Expected outcome is the system doesn't crash but simply yields the same postcode invalid message in the event of the API failing.

#### Result 1

Test passed no issues.

#### Test 2 Description

1. Line 77 in home app views file, remove '+user_lat+' from 'distance_url'.
2. Repeat stages 2 - 4 of test 1.
3. Undo stage 1 to reset view back to original state.

Expected outcome is the system doesn't crash but simply yields the same postcode invalid message in the event of the API failing.

#### Result 2

Test passed no issues.

# Deployment
## View website

if you simply want to view the site then please visit:<br>
https://doms-burger-joint.herokuapp.com/

## Setting up remote database

- In settings add "import dj_database_url".
- Set default database to read from the config variable in heroku or whichever platform used to deploy your app (settings, 114-116).
- Can set up database config in an if statement depending on whether the app is running in heroku or not.
- Run migrations again in CLI: python3 manage.py migrate
- Load products in CLI, starting with those which have no dependencies: python3 manage.py loaddata [name_of_fixture]
- Run command above for food_categories, food_combos & food_items.

## Storing Static Files to the Cloud

- Prevent heroku from attempting to collect static files (in CLI): heroku config:set DISABLE_COLLECTSTATIC=1 --app [app_name]
- (in CLI) pip3 install whitenoise
- Add whitenoise middleware to middleware config (settings, 50)
- Add session storage variable to settings (line 173).
- python3 manage.py collectstatic

## Deploy to Heroku

- Set app as an allowed host for heroku (settings, 25).
- Generate secret key (using https://miniwebtool.com/wordpress-secret-key-generator/) 
  then add to heroku config vars and also to your local environment variables.
- Ensure the secret key is not revealed anywhere in the code as this will potentially be exposed in github.
- Commit your changes and push to heroku.
- In your heroku app page navigate to the 'Deploy' tab and then 'Deployment method' section. 
  Here you will have the opportunity to automatically deploy your app whenever you push to github.
- Ensure Django 'DEBUG' variable is set equal to False before deploying to Heroku.

# Credits


## Content 
## Media
## Code

def changeform_link(self) method in OrderLineItem Models (Checkout)
Resource: https://stackoverflow.com/questions/2857001/adding-links-to-full-change-forms-for-inline-items-in-django-admin
Solution: answered May 27 '10 at 22:25, Lukasz Korzybski
                
        django pagination in Members area profile page and view (Members Area)

## Acknowledgements

I would like to thank my mentor Brian and all the staff at Code Institute for their support.