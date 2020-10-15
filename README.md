# DataExample validation and Schmea generation API

You can get more `Schema` examples here:
https://standards-ontotest.oftrust.net/v2/Schema/DataProductOutput

and `DataExample` examples here: 
https://standards-ontotest.oftrust.net/v2/DataExample/DataProductOutput


# DataExample validation endpoint
### Prerequirements:
* `Schema` have to be deployed to https://standards-ontotest.oftrust.net/v2/

### To validate DataExample, Send POST request with `DataExample` json body:
```bash
curl -X POST http://127.0.0.1:8000/api/validate -H 'Content-Type: application/json' -d 
'{
	"@context": "https://standards-ontotest.oftrust.net/v2/Context/DataProductOutput/",
	"data": {},
	"signature": {
		"created": "2018-11-22T12:00:00Z",
		"creator": "https://example.org/creator/public_key.pub",
		"signatureValue": "eyJ0eXAiOiJK...gFWFOEjXk",
		"type": "RsaSignature2018"
	}
}'
```
### If data example is valid, you wil get:
```
{
    "isValid": "True"
}
```
### Otherwise:
```
{
    "error": {
        "status": 422,
        "error": "UNPROCESSABLE_ENTITY_EXCEPTION",
        "description": "One or more fields raised validation errors",
        "fields": {
            "missing_key": "is a required property"
        }
    }
}
```
# DataProduct schema generation endpoint:
### To generate `Schema`, send POST request with `DataExample` json body:
```bash
curl -X POST http://127.0.0.1:8000/api/schema -H 'Content-Type: application/json' -d 
'{
	"@context": "https://standards-ontotest.oftrust.net/v2/Context/DataProductOutput/",
	"data": {},
	"signature": {
		"created": "2018-11-22T12:00:00Z",
		"creator": "https://example.org/creator/public_key.pub",
		"signatureValue": "eyJ0eXAiOiJK...gFWFOEjXk",
		"type": "RsaSignature2018"
	}
}'
```
### If data example is valid, you wil get DataProduct `Schema`:
```
{
    "$id": "https://standards-ontotest.oftrust.net/v2/Schema/DataProductOutput/",
    "$schema": "http://json-schema.org/draft-06/schema#",
    "properties": {
        "@context": {
            "$id": "#/properties/@context",
            "const": "https://standards-ontotest.oftrust.net/v2/Context/DataProductOutput/?v=2.0",
            "description": "",
            "title": "",
            "type": "string"
        },
        "data": {
            "$id": "#/properties/data",
            "description": "",
            "title": "",
            "type": "object"
        },
        "signature": {
            "$id": "#/properties/signature",
            "description": "",
            "properties": {
                "created": {
                    "$id": "#/properties/signature/properties/created",
                    "description": "Creation time",
                    "title": "Created",
                    "type": "string"
                },
                "creator": {
                    "$id": "#/properties/signature/properties/creator",
                    "description": "",
                    "title": "",
                    "type": "string"
                },
                "signatureValue": {
                    "$id": "#/properties/signature/properties/signatureValue",
                    "description": "",
                    "title": "",
                    "type": "string"
                },
                "type": {
                    "$id": "#/properties/signature/properties/type",
                    "description": "",
                    "title": "",
                    "type": "string"
                }
            },
            "required": [
                "created",
                "creator",
                "signatureValue",
                "type"
            ],
            "title": "",
            "type": "object"
        }
    },
    "required": [
        "@context",
        "data",
        "signature"
    ],
    "type": "object"
}
```

# Http Status Codes
### Success 2xx
- [200](http://httpstatuses.com/200) - **Ok** - The request was fulfilled.
### Client side errors 4xx
- [400](http://httpstatuses.com/400) - **Bad Request** - Bad request syntax or unsupported method.
- [404](http://httpstatuses.com/404) - **Not Found** - Nothing matches the given URI.
- [415](http://httpstatuses.com/415) - **Unsupported Media Type** - Entity body in unsupported format.
- [422](http://httpstatuses.com/422) - **Unprocessable Entity** - Information in the request body can't be parsed or understood.

# Run with Docker
```
docker build --tag ontology-api:1.0 .

docker run --publish 8000:5000 --detach ontology-api:1.0
```