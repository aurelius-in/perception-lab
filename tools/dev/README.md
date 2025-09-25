# Local dev helpers

- Start FastAPI (example):

```bash
uvicorn service.api:app --reload --port 8080
```

- Ingest a local PDF (example payload):

```json
{
  "dataset_id": "sample-docs",
  "uris": ["./docs/sample.pdf"],
  "metadata": {"source": "local"}
}
```
