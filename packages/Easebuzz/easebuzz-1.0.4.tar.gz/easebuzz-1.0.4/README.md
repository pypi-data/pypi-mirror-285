# Easebuzz Payment Gateway Integration Library - Python

This Python library provides functionalities to integrate the Easebuzz Payment Gateway into your web application. With this library, you can initiate payments, query transaction details, perform refunds, manage payouts, and verify Easebuzz API responses.

# How to use - Example use case

## 1. Import EasebuzzAPIs
```from Easebuzz import EasebuzzAPIs```

## 2. Initialize the EasebuzzAPIs class
```easebuzz_api = EasebuzzAPIs(your_merchant_key, your_salt_key, env)```

## 3. Prepare Payment parameters
```
payment_params = {
    'amount': '10',
    'firstname': 'Deevek',
    'email': 'deevek@world.com',
    'phone': '9999999999',
    'productinfo': 'Apple Iphone',
    'surl': 'https://example.com/success',
    'furl': 'https://example.com/failure'
}
```

## 4. Initiate payment
```
response = easebuzz_api.initiate_payment_api(payment_params)
print(response)
```

