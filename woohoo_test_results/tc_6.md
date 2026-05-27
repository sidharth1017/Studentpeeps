# Test Case #6: Success - Cardnumber & Card PIN
Quantity >=5

**API:** Order API
**Input:**
```
Product SKU: CNPIN
Amount: 1000
delivery_mode = API 
sync_only = false
qty >=5
```

**Request Body:**
```json
{
  "address": {
    "firstname": "Test",
    "lastname": "User",
    "email": "hi@studentpeeps.club",
    "telephone": "+919876543210",
    "country": "IN",
    "billToThis": true
  },
  "billing": {
    "firstname": "Test",
    "lastname": "User",
    "email": "hi@studentpeeps.club",
    "telephone": "+919876543210",
    "country": "IN"
  },
  "deliveryMode": "API",
  "payments": [
    {
      "code": "svc",
      "amount": 5000
    }
  ],
  "products": [
    {
      "sku": "CNPIN",
      "price": 1000,
      "qty": 5,
      "currency": 356
    }
  ],
  "refno": "STEST_6_1778958926",
  "syncOnly": false
}
```

**Response:**
```json
{
  "status": "PROCESSING",
  "orderId": "ABF5552058832",
  "refno": "STEST_6_1778958926",
  "cancel": {
    "allowed": false
  },
  "currency": {
    "code": "INR",
    "numericCode": "356",
    "symbol": "\u20b9"
  },
  "payments": [
    {
      "code": "svc",
      "balance": "9923078.0000"
    }
  ]
}
```
