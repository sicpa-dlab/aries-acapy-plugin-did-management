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
  - didweb
```

and run aca-py from the poetry environment:
```bash
poetry env
aca-py ....
```

## Creating a did:web

```bash
curl -X 'POST' \
  'http://localhost:7082/wallet/did/create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "method": "web",
  "options": {
    "did": "did:web:adaptivespace.io",
    "key_type": "ed25519"
  }
}'
```

results in

```json
{
  "result": {
    "did": "did:web:adaptivespace.io",
    "verkey": "FLgVvRqfE1iATV315ySYojoz3SqQ2zJMGyvjDynyErm5",
    "posture": "wallet_only",
    "key_type": "ed25519",
    "method": "web"
  }
}
```

# Fetching the DIDDoc

```bash
curl -X 'GET' \
  'http://localhost:7082/didweb/diddoc?did=did%3Aweb%3Aadaptivespace.io' \
  -H 'accept: application/json'
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
      "type": "JsonWebKey2020",
      "controller": "did:web:adaptivespace.io",
      "publicKeyJwk": {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "1Q5QR+Y/iFKv42AnAC8sgMlFTrDfyZbFbm7SSBrpaog="
      }
    }
  ],
  "authentication": [
    "did:web:adaptivespace.io#key-1"
  ],
  "assertionMethod": [
    "did:web:adaptivespace.io#key-1"
  ]
}
```

Notes:
* service endpoint is not listed yet


# Rotate key
```bash
curl -X 'PUT' \
  'http://localhost:7082/didweb/rotate?did=did%3Aweb%3Aadaptivespace.io' \
  -H 'accept: application/json'
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
      "type": "JsonWebKey2020",
      "controller": "did:web:adaptivespace.io",
      "publicKeyJwk": {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "1Q5QR+Y/iFKv42AnAC8sgMlFTrDfyZbFbm7SSBrpaog="
      }
    },
    {
      "id": "did:web:adaptivespace.io#key-2",
      "type": "JsonWebKey2020",
      "controller": "did:web:adaptivespace.io",
      "publicKeyJwk": {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "kFSu1+YV7vDD/8GeQ3cpKJi+b5ywocJSbMZepzWXqhE="
      }
    }
  ],
  "authentication": [
    "did:web:adaptivespace.io#key-1",
    "did:web:adaptivespace.io#key-2"
  ],
  "assertionMethod": [
    "did:web:adaptivespace.io#key-1",
    "did:web:adaptivespace.io#key-2"
  ]
}
```
