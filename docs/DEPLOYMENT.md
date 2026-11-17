# Production Deployment Guide

This guide details steps to containerize and deploy the **AI-Powered Customer Support Agent** to cloud platforms such as Render, Railway, Docker, or AWS.

---

## 1. Production WSGI Server

In production environments, run Flask behind a production-grade WSGI server such as **Gunicorn** (Linux/macOS) or **Waitress** (Windows).

### Linux (Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app('production')"
```

### Windows (Waitress):
```bash
pip install waitress
waitress-serve --port=5000 --call backend.app:create_app
```

---

## 2. Docker Deployment

### Dockerfile
Create a `Dockerfile` in the root of the project:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5000

ENV FLASK_ENV=production
ENV PORT=5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:create_app('production')"]
```

### Build & Run Docker Container
```bash
docker build -t ai-customer-support .
docker run -p 5000:5000 --env-file .env ai-customer-support
```

---

## 3. Deploying to Cloud Platforms

### Render / Railway
1. Push repository to GitHub.
2. In Render/Railway dashboard, choose **New Web Service** connected to your repo.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT "backend.app:create_app('production')"`
5. In Environment Variables, configure:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `DB_MODE=supabase`

---

## 4. Production Security Checklist

- [ ] **HTTPS/TLS Enforced**: Ensure all traffic runs through TLS 1.3.
- [ ] **Secure Secret Keys**: Generate cryptographically random 64-character keys for `SECRET_KEY` and `JWT_SECRET_KEY`.
- [ ] **Supabase RLS Enabled**: Verify all 12 tables have Row Level Security enabled with `database/rls_policies.sql`.
- [ ] **Rate Limiting**: Monitor sliding window rate limiter thresholds against DDoS.
- [ ] **Upload Size Limits**: Ensure reverse proxy (Nginx / Cloudflare) caps uploads at 16MB.
