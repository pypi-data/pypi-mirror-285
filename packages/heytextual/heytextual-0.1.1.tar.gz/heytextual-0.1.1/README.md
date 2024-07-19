# HeyTextual Python SDK

Este repositorio contiene el SDK de Python para la API de HeyTextual.

## Installación

```bash
pip install heytextual
```

## Uso

Puedes encontrar más información en la API reference de nuestro website.

Ejemplo:
```python
import heytextual

client = heytextual.HeyTextualClient(api_key="your_api_key")

data = heytextual.extract("/path/to/file", "AUTO")

documents = heytextual.documents(limit=20)

document = heytextual.document(document_id="DOCUMENTID")

templates = heytextual.templates(limit=20)
```
