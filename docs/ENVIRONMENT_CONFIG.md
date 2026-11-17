# Environment Configuration Guide

This guide details all environment variables supported by the **AI-Powered Customer Support Agent** application.

---

## 1. Quick Setup

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

## 2. Environment Variables Reference

| Variable | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Optional | `development` | Running environment: `development`, `testing`, `production` |
| `HOST` | Optional | `127.0.0.1` | Network interface for Flask listener |
| `PORT` | Optional | `5000` | HTTP port for server |
| `SECRET_KEY` | **Recommended** | `dev-secret-key-...` | Flask session cookie encryption key |
| `JWT_SECRET_KEY` | **Required** | `jwt-super-secret-...`| HS256 secret key for signing user authentication tokens (must be >= 32 chars) |
| `JWT_ACCESS_TOKEN_EXPIRES`| Optional | `86400` | Token lifetime in seconds (default: 24 hours) |
| `GEMINI_API_KEY` | **Recommended** | `""` | Google Gemini API key from [Google AI Studio](https://aistudio.google.com/). If omitted, operates in local synthesis mode |
| `GEMINI_MODEL` | Optional | `gemini-1.5-flash` | Gemini generation model (`gemini-1.5-flash`, `gemini-2.0-flash`) |
| `GEMINI_EMBEDDING_MODEL` | Optional | `text-embedding-004` | Gemini vector embedding model for document chunking |
| `SUPABASE_URL` | Optional | `""` | Supabase project API URL (e.g. `https://xyz.supabase.co`) |
| `SUPABASE_KEY` | Optional | `""` | Supabase `anon` public key |
| `SUPABASE_SERVICE_ROLE_KEY`| Optional | `""` | Supabase `service_role` private key for admin operations |
| `DB_MODE` | Optional | `auto` | Database engine mode: `auto`, `supabase`, or `sqlite` |
| `UPLOAD_FOLDER` | Optional | `uploads` | Local directory for storing uploaded customer documents and knowledge PDFs |
