# monetize
 A python library to make some money

## Install
 pip install monetize

## See example.py for how to use

## Creating a subscription
    1. Create a Stripe account
    2. Configure your business to accept payments
    3. Go to the Developers section
    4. Click API Keys
    5. Select "Create Secret Key"
    6. Configure this key to your liking
    7. Save this key to authenticate in your code later
    8. Create a customer (you'll need to do this for each billable user)
    9. Go to Product Catalog
    10. Create a new product with the following settings
        1. Recurring
        2. Usage-based per-unit pricing model
        3. Pick your price
        4. Pick sum of usage values during period for usage (if desired)
        5. Billing period monthly (if desired)
        6. Select Create
    11. Create a subscription
    12. Assign a user
    13. Assign the product from step 5
    14. Go to the newly made subscription page
    15. Copy the **Subscription Item ID** (note: this is not the Subscription ID)
    16. Use this ID in your code to accrue to that account
    17. Profit
