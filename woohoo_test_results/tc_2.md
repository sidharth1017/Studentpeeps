# Test Case #2: Oauth Token Generation - Valid credentials

**API:** Oauth flow
**Input:**
```
Token to be generated using the valid credentials provided.
Token once generated should be stored and retrieved untill token rejected response is received.
```

**Request Body:**
```json
N/A
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb25zdW1lcklkIjo5ODIsImV4cCI6MTc3OTQ0MjgxNywidG9rZW4iOiIzZTI0YTI2ZjZkZWMxMmEwZWRmMWJhY2FkOWJiYzU5MSJ9.lCD14J_FrE8hSWRjdukyMaodkHGDwuMEoKdw3vvXJog"
}
```
