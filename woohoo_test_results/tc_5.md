# Test Case #5: Success - Cardnumber & Card PIN
Quantity <=4

**API:** Order API
**Input:**
```
Product SKU: CNPIN
Amount: 1000
delivery_mode = API 
sync_only = true
qty = 1 or <=4
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
      "amount": 1000
    }
  ],
  "products": [
    {
      "sku": "CNPIN",
      "price": 1000,
      "qty": 1,
      "currency": 356
    }
  ],
  "refno": "STEST_5_1778958905",
  "syncOnly": true
}
```

**Response:**
```json
{
  "status": "COMPLETE",
  "orderId": "ABF5552058830",
  "refno": "STEST_5_1778958905",
  "cancel": {
    "allowed": true,
    "allowedWithIn": 15
  },
  "currency": {
    "code": "INR",
    "numericCode": "356",
    "symbol": "\u20b9"
  },
  "payments": [
    {
      "code": "svc",
      "balance": "9928078.0000"
    }
  ],
  "cards": [
    {
      "sku": "CNPIN",
      "productName": "API TESTING - CN & PIN",
      "labels": {
        "cardNumber": "Gift Card Number",
        "cardPin": "Card PIN",
        "merchantCardNumber": "",
        "activationCode": "",
        "samsungWalletLabel": "",
        "sequenceNumber": "",
        "validity": "Validity"
      },
      "cardNumber": "8090920016120254",
      "cardPin": "189384",
      "merchantCardNumber": null,
      "senderName": "",
      "activationCode": null,
      "barcode": "",
      "activationUrl": null,
      "redemptionUrl": {
        "label": "",
        "url": ""
      },
      "addToSamsungWallet": "",
      "formats": [
        {
          "key": "CNONLY",
          "value": "8090920016120254"
        },
        {
          "key": "TRACK2",
          "value": ";8090920016120254=054600001016897?"
        },
        {
          "key": "QCBARCODE-26-V1",
          "value": "18009019200011661280295470"
        }
      ],
      "amount": "1000.00",
      "redemptionStartDate": "",
      "validity": "2027-05-17T00:45:21+05:30",
      "issuanceDate": "2026-05-16T19:15:21+00:00",
      "sequenceNumber": "",
      "cardId": 6932681,
      "recipientDetails": {
        "salutation": null,
        "name": "TEST USER",
        "firstname": "TEST",
        "lastname": "USER",
        "email": "HI@STUDENTPEEPS.CLUB",
        "mobileNumber": "+919876543210",
        "status": "",
        "failureReason": "",
        "delivery": {
          "mode": "API",
          "status": {
            "sms": {
              "status": "NA",
              "reason": "NA"
            },
            "email": {
              "status": "NA",
              "reason": "NA"
            }
          }
        }
      },
      "theme": ""
    }
  ],
  "products": {
    "CNPIN": {
      "sku": "CNPIN",
      "name": "API TESTING - CN & PIN",
      "balanceEnquiryInstruction": null,
      "specialInstruction": "",
      "images": {
        "thumbnail": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CNPIN/d/thumbnail/324_microsite.png",
        "mobile": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CNPIN/d/mobile/324_microsite.png",
        "base": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CNPIN/d/image/324_microsite.png",
        "small": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CNPIN/d/small_image/324_spayapi.png"
      },
      "cardBehaviour": "QC"
    }
  },
  "additionalTxnFields": []
}
```
