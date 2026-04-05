# Deployment Information

## Deployment URL

**Live Application:** https://rag-policy-assistant.onrender.com

## Platform

- **Host**: Render (free tier)
- **Service type**: Web Service

## Configuration

- Environment variables configured via Render dashboard:
  - `OPENROUTER_API_KEY` — LLM API key (OpenRouter free tier)
  - `OPENROUTER_MODEL` — `openai/gpt-oss-20b:free`
- Automatic deployment on push to `main` branch (via GitHub Actions CI/CD)
- Health check: `/health`

## Access

Public URL: **https://rag-policy-assistant.onrender.com**

## Notes

- The app uses a background warmup on first request. Allow ~30 seconds for
  the pipeline to initialize before the first answer.
- The vectorstore is pre-built and committed to the repository.
- Free-tier instances may spin down after inactivity; the first request after
  a cold start will take longer.

