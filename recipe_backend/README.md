# Recipe Backend

This FastAPI service powers the Recipe Hub API.

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## CORS
CORS origins are configured from `CORS_ORIGINS` env var (comma-separated). Defaults include:
- http://localhost:3000
- http://127.0.0.1:3000
- Optional `PREVIEW_URL` environment variable is also allowed if set.

## Database
Uses `DATABASE_URL` (default sqlite:///./recipes.db). Tables are auto-created on startup for development.

## Regenerate OpenAPI
Run the app (so routes are loaded), then generate the schema file:
```bash
uvicorn src.api.main:app --port 3001 --reload &
python -m src.api.generate_openapi
```
This writes `interfaces/openapi.json`.
