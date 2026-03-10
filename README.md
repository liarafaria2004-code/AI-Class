# AI-Class

Minimal notes/query service with in-memory storage and a Gemini client abstraction.

## Run in browser

```bash
python -m ai_class.http_server
```

Then open:

- `http://127.0.0.1:8000/` (API landing page)
- `http://127.0.0.1:8000/health`

## Example API calls

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H 'Content-Type: application/json' \
  -d '{"text":"hello world","tags":["ai"]}'

curl -X POST http://127.0.0.1:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"hello","top_k":1}'
```
