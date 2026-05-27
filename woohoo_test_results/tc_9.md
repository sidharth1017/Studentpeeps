# Test Case #9: Success - Amazon ( 16 Digit Cardnumber & 14 Digit Card PIN)

**API:** Order API
**Input:**
```
SKU ID: CLAIMCODE
Amount: 1000
sync_only = true / false (Refer Test case 1&2 for the diff & pass accordingly as per the implementation)
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
      "sku": "CLAIMCODE",
      "price": 1000,
      "qty": 1,
      "currency": 356
    }
  ],
  "refno": "STEST_9_1778958931",
  "syncOnly": true
}
```

**Response:**
```json
{
  "status": "COMPLETE",
  "orderId": "ABF5552058836",
  "refno": "STEST_9_1778958931",
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
      "balance": "9921078.0000"
    }
  ],
  "cards": [
    {
      "sku": "CLAIMCODE",
      "productName": "API TESTING - Claim Code",
      "labels": {
        "cardNumber": "GC ID",
        "cardPin": "Claim code",
        "merchantCardNumber": "",
        "activationCode": "Activation Code",
        "samsungWalletLabel": "",
        "sequenceNumber": "",
        "validity": "Validity"
      },
      "cardNumber": "8090920032364180",
      "cardPin": "WHCMV6UYGRJJUNTD",
      "merchantCardNumber": null,
      "senderName": "",
      "activationCode": null,
      "barcode": null,
      "activationUrl": null,
      "redemptionUrl": {
        "label": "",
        "url": ""
      },
      "addToSamsungWallet": "",
      "formats": [
        {
          "key": "CNONLY",
          "value": "8090920032364180"
        }
      ],
      "amount": "1000.00",
      "redemptionStartDate": "",
      "validity": "2027-05-17T00:45:33+05:30",
      "issuanceDate": "2026-05-16T19:15:33+00:00",
      "sequenceNumber": "",
      "cardId": 6932688,
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
    "CLAIMCODE": {
      "sku": "CLAIMCODE",
      "name": "API TESTING - Claim Code",
      "balanceEnquiryInstruction": null,
      "specialInstruction": "",
      "images": {
        "thumbnail": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CLAIMCODE/d/thumbnail/327_microsite.jpg",
        "mobile": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CLAIMCODE/d/mobile/327_microsite.jpg",
        "base": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CLAIMCODE/d/image/327_microsite.jpg",
        "small": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/CLAIMCODE/d/small_image/327_spayapi.png"
      },
      "cardBehaviour": "QC"
    }
  },
  "additionalTxnFields": []
}
```
