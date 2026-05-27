# Test Case #3: Oauth request - Invalid Credentials

**API:** Oauth flow
**Input:**
```
Invalid/ wrong token can be used.
(or)
Tokens can be generated using the same credentials and old tokens to be triggered with the request.

```

**Request Body:**
```json
N/A
```

**Response:**
```json
HTTP 400: 
{"code":8302,"message":"Invalid Client ID ","messages":[]}
```
