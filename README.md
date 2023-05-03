# ACA-Python DID Web plugin

## Developing

First-time initialization of the python environment:

```bash
poetry install
pre-commit install
```

You're all set !

To run aca-py with the plugin, include it in your config:

```yaml
plugin:
  - didmanagement
```

and run aca-py from the poetry environment:
```bash
poetry env
aca-py ....
```
# Fetching the DIDDoc

```bash
curl -X 'GET' \
  'http://localhost:3001/wallet/did%3Aweb%3Aadaptivespace.io/diddoc?number_of_keys=1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiI5ZWI4MzU5Yi05YzAwLTRlNWYtODg5Mi04ZmE1YTYxZWQyZjAiLCJpYXQiOjE2ODMxMTYzMzR9.qVPrNFZrtNiApNu6ByljnuKEJyQ1Yv4K4bAFTeXUYbs'
```

results in

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1"
  ],
  "id": "did:web:adaptivespace.io",
  "controller": [
    "did:web:adaptivespace.io"
  ],
  "verificationMethod": [
    {
      "id": "did:web:adaptivespace.io#key-1",
      "type": "Ed25519VerificationKey2018",
      "controller": "did:web:adaptivespace.io",
      "publicKeyBase58": "BjHQU69pvfDdzM1Dh1CA19dSmK3P9nYP5SKvyQvrsAYq"
    }
  ],
  "authentication": [
    "did:web:adaptivespace.io#key-1"
  ],
  "assertionMethod": [
    "did:web:adaptivespace.io#key-1"
  ],
  "service": [
    {
      "id": "did:web:adaptivespace.io#service-0",
      "type": "did-communication",
      "serviceEndpoint": "http://localhost:3000",
      "recipientKeys": [
        "did:web:adaptivespace.io#key-1"
      ],
      "routingKeys": [],
      "priority": 0
    }
  ]
}
```
    

# Rotate key
```bash
curl -X 'PUT' \
  'http://localhost:3001/wallet/did%3Aweb%3Aadaptivespace.io/rotate-keys' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiI5ZWI4MzU5Yi05YzAwLTRlNWYtODg5Mi04ZmE1YTYxZWQyZjAiLCJpYXQiOjE2ODMxMTYzMzR9.qVPrNFZrtNiApNu6ByljnuKEJyQ1Yv4K4bAFTeXUYbs'
```

results in the updated DIDDoc:

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1"
  ],
  "id": "did:web:adaptivespace.io",
  "controller": [
    "did:web:adaptivespace.io"
  ],
  "verificationMethod": [
    {
      "id": "did:web:adaptivespace.io#key-1",
      "type": "Ed25519VerificationKey2018",
      "controller": "did:web:adaptivespace.io",
      "publicKeyBase58": "BjHQU69pvfDdzM1Dh1CA19dSmK3P9nYP5SKvyQvrsAYq"
    },{
		"id": "did:web:adaptivespace.io#key-2",
		"type": "Ed25519VerificationKey2018",
		"controller": "did:web:adaptivespace.io",
		"publicKeyBase58": "D8VqpiMhCr1oXsMiBZPqYx8ND83UruHLcmJysNrSRqxX"
	}
  ],
  "authentication": [
    "did:web:adaptivespace.io#key-1",
    "did:web:adaptivespace.io#key-2"
  ],
  "assertionMethod": [
    "did:web:adaptivespace.io#key-1",
    "did:web:adaptivespace.io#key-2"
  ],
  "service": [
    {
      "id": "did:web:adaptivespace.io#service-0",
      "type": "did-communication",
      "serviceEndpoint": "http://localhost:3000",
      "recipientKeys": [
        "did:web:adaptivespace.io#key-2"
      ],
      "routingKeys": [],
      "priority": 0
    }
  ]
}
```

# Register route
```bash
curl -X 'PUT' \
  'http://localhost:3001/wallet/did%3Aweb%3Aadaptivespace.io/routing/register-route' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiI5ZWI4MzU5Yi05YzAwLTRlNWYtODg5Mi04ZmE1YTYxZWQyZjAiLCJpYXQiOjE2ODMxMTYzMzR9.qVPrNFZrtNiApNu6ByljnuKEJyQ1Yv4K4bAFTeXUYbs'
```

results in HTTP response 201 and empty body which means success.

# Mark public

```bash
curl -X 'PUT' \
  'http://localhost:3001/wallet/did%3Aweb%3Aadaptivespace.io/mark-public' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiI5ZWI4MzU5Yi05YzAwLTRlNWYtODg5Mi04ZmE1YTYxZWQyZjAiLCJpYXQiOjE2ODMxMTYzMzR9.qVPrNFZrtNiApNu6ByljnuKEJyQ1Yv4K4bAFTeXUYbs'
```

results in:

```json
{
  "did": "did:web:adaptivespace.io",
  "verkey": "BjHQU69pvfDdzM1Dh1CA19dSmK3P9nYP5SKvyQvrsAYq",
  "posture": "posted",
  "key_type": "ed25519",
  "method": "web"
}
```
