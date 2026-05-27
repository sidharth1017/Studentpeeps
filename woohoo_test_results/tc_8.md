# Test Case #8: Success - Card no only / Voucher code

**API:** Order API
**Input:**
```
SKU ID: VOUCHERCODE
Amount: 1000.
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
      "sku": "VOUCHERCODE",
      "price": 1000,
      "qty": 1,
      "currency": 356
    }
  ],
  "refno": "STEST_8_1778958929",
  "syncOnly": true
}
```

**Response:**
```json
{
  "status": "COMPLETE",
  "orderId": "ABF5552058834",
  "refno": "STEST_8_1778958929",
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
      "balance": "9922078.0000"
    }
  ],
  "cards": [
    {
      "sku": "VOUCHERCODE",
      "productName": "API TESTING - Voucher code",
      "labels": {
        "cardNumber": "",
        "cardPin": "Voucher Code",
        "merchantCardNumber": "",
        "activationCode": "",
        "samsungWalletLabel": "",
        "sequenceNumber": "",
        "validity": "Validity"
      },
      "cardNumber": null,
      "cardPin": "PINETEST16760",
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
          "value": "8090921090695675"
        }
      ],
      "amount": "1000.00",
      "redemptionStartDate": "",
      "validity": "2026-10-31T00:00:00+05:30",
      "issuanceDate": "2026-05-16T19:15:30+00:00",
      "sequenceNumber": "",
      "cardId": 6932687,
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
    "VOUCHERCODE": {
      "sku": "VOUCHERCODE",
      "name": "API TESTING - Voucher code",
      "balanceEnquiryInstruction": null,
      "specialInstruction": "",
      "images": {
        "thumbnail": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/VOUCHERCODE/d/thumbnail/325_microsite.jpg",
        "mobile": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/VOUCHERCODE/d/mobile/325_microsite.jpg",
        "base": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/VOUCHERCODE/d/image/325_microsite.jpg",
        "small": "https://d1ssr5uvl3uuv0.cloudfront.net/uat/product/VOUCHERCODE/d/small_image/325_spayapi.jpg"
      },
      "cardBehaviour": "QC"
    }
  },
  "additionalTxnFields": []
}
```
