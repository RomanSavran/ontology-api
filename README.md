
# DataExample validation endpoint

```
/validate
```
### Send POST request with DataExample json body 
```
{
	"@context": "https://standards-ontotest.oftrust.net/v2/Context/DataProductOutput/",
	"data": {},
	"signature": {
		"created": "2018-11-22T12:00:00Z",
		"creator": "https://example.org/creator/public_key.pub",
		"signatureValue": "eyJ0eXAiOiJK...gFWFOEjXk",
		"type": "RsaSignature2018"
	}
}
```
##### <i>Schema have to be deployed</i>
### If data example is valid, you wil get:
```
{
    "isValid": "True"
}
```
### Otherwise:
```
{
    "errors": [
        "Error details..."
    ],
    "isValid": "False"
}
```
<br>

# DataProduct schema generation endpoint
```
/schema
```
### Send POST request with DataExample json body:

```
{
	"@context": "https://standards-ontotest.oftrust.net/v2/Context/DataProductOutput/",
	"data": {},
	"signature": {
		"created": "2018-11-22T12:00:00Z",
		"creator": "https://example.org/creator/public_key.pub",
		"signatureValue": "eyJ0eXAiOiJK...gFWFOEjXk",
		"type": "RsaSignature2018"
	}
}
```
### If data example is valid, you wil get DataProduct schema:
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