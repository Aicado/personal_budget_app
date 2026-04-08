# YNAB Analyzer - Deployment Guide

## 🚀 Deployment Options

### 1. Local Development

```bash
# Install dependencies
make setup

# Run development servers
make dev

# Or run separately:
make dev-backend  # Terminal 1
make dev-frontend # Terminal 2
```

Open `http://localhost:5173` in your browser.

### 2. Docker Deployment (Single Container)

```bash
# Build Docker image
docker build -t ynab-analyzer .

# Run container
docker run -p 8000:8000 -v $(pwd)/ynab_data:/app/ynab_data ynab-analyzer
```

Access the app at `http://localhost:8000`

### 3. Docker Compose

```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### 4. Production Build

```bash
# Build optimized frontend
npm run build

# Build Python wheel
uv build

# Deploy backend
uv run -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
```

## 🌐 Production Deployment Options

### Heroku

```bash
# Create app
heroku create ynab-analyzer

# Add buildpacks
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

# Deploy
git push heroku main
```

### AWS

1. **Frontend (S3 + CloudFront)**
   - Build: `npm run build`
   - Upload `dist/` to S3
   - Set up CloudFront distribution

2. **Backend (EC2/Lambda)**
   - Option A: EC2 with Python 3.10
   - Option B: AWS Lambda with API Gateway

### Google Cloud

```bash
# Deploy to Cloud Run
gcloud run deploy ynab-analyzer \
  --source . \
  --port 8000 \
  --region us-central1
```

### DigitalOcean

```bash
# Using App Platform
doctl apps create --spec app.yaml
```

## 📋 Environment Variables

Create a `.env` file for sensitive configuration:

```env
# Backend
DEBUG=false
API_WORKERS=4
CORS_ORIGINS=https://yourdomain.com

# Frontend (build-time only)
VITE_API_URL=https://api.yourdomain.com
```

## 🔒 Security Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS only
- [ ] Restrict CORS origins
- [ ] Add authentication/authorization
- [ ] Use environment variables for secrets
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Use database encryption if storing data
- [ ] Set up monitoring and alerts
- [ ] Regular security updates

## 📊 Monitoring & Logging

### Backend Monitoring
```bash
# Prometheus metrics
pip install prometheus-client

# Logging with JSON output
pip install python-json-logger
```

### Frontend Monitoring
```bash
# Add Sentry for error tracking
npm install @sentry/react
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Build
        run: |
          make build
          uv build
      
      - name: Deploy
        run: docker-compose up -d
```

## 🗄️ Database Setup (Optional)

If adding persistent storage:

```bash
# PostgreSQL
docker run -d \
  --name ynab-db \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15
```

Update `pyproject.toml`:
```toml
dependencies = [
    # ... existing deps
    "sqlalchemy==2.0.23",
    "psycopg2-binary==2.9.9",
]
```

## 📈 Scaling Recommendations

1. **Frontend**: Use CDN (CloudFlare, CloudFront)
2. **Backend**: Run multiple uvicorn workers
3. **Database**: Read replicas for analytics queries
4. **Cache**: Redis for frequent queries
5. **Storage**: S3/Cloud Storage for uploads

## 🆘 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Build fails
```bash
# Clean and rebuild
make clean
make build
```

### Memory issues
```bash
# Increase available memory
# Docker: update docker-compose.yml with `mem_limit`
# Or use lighter dependencies
```

## 📞 Support

For deployment issues, check:
- Application logs: `docker logs <container-id>`
- Browser console for frontend errors
- Backend error responses in Network tab
- System resources: `docker stats`

---

Happy deploying! 🚀
