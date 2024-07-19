# HeyTextual Python SDK

Este repositorio contiene el SDK de Python para la API de HeyTextual.

## Installación

pip install heytextual

## Uso

Puedes encontrar más información en la API reference de nuestro website.

Ejemplo:

import redacted

client = redacted.RedactedClient(api_key="your_api_key")

data = client.extract("/path/to/file", "AUTO")

documents = client.documents(limit=20)

document = client.document(document_id="DOCUMENTID")

templates = client.templates(limit=20)
