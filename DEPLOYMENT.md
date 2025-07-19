# TechPal Deployment Guide

This guide covers deploying TechPal to various hosting platforms.

## 🚀 Quick Deployment Options

### 1. Railway (Recommended for MVP)

Railway is perfect for quick deployment with automatic scaling.

#### Steps:
1. **Fork/Clone** this repository to your GitHub account
2. **Sign up** at [Railway](https://railway.app/)
3. **Connect** your GitHub repository
4. **Add Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   DATABASE_URL=postgresql://... (Railway will provide)
   ```
5. **Deploy** - Railway will automatically detect and deploy your FastAPI app

#### Railway Configuration:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

### 2. Render

Render offers a free tier with PostgreSQL support.

#### Steps:
1. **Sign up** at [Render](https://render.com/)
2. **Create New Web Service**
3. **Connect** your GitHub repository
4. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.9+
5. **Add Environment Variables** (same as Railway)
6. **Add PostgreSQL Database** (optional, for production)

### 3. Heroku

Traditional hosting with add-ons.

#### Steps:
1. **Install Heroku CLI**
2. **Create Heroku app**:
   ```bash
   heroku create your-techpal-app
   ```
3. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```
4. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set ANTHROPIC_API_KEY=your_key
   ```
5. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  techpal:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/techpal
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=techpal
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run
```bash
# Build image
docker build -t techpal .

# Run with Docker Compose
docker-compose up -d

# Or run standalone
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key techpal
```

## ☁️ Cloud Platform Deployment

### Google Cloud Run

1. **Install Google Cloud SDK**
2. **Build and push image**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/techpal
   ```
3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy techpal \
     --image gcr.io/PROJECT_ID/techpal \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### AWS Elastic Beanstalk

1. **Create application**:
   ```bash
   eb init techpal --platform python-3.9
   ```
2. **Create environment**:
   ```bash
   eb create techpal-env
   ```
3. **Set environment variables** in AWS Console
4. **Deploy**:
   ```bash
   eb deploy
   ```

### Azure App Service

1. **Install Azure CLI**
2. **Create resource group**:
   ```bash
   az group create --name techpal-rg --location eastus
   ```
3. **Create app service plan**:
   ```bash
   az appservice plan create --name techpal-plan --resource-group techpal-rg --sku B1
   ```
4. **Create web app**:
   ```bash
   az webapp create --name techpal-app --resource-group techpal-rg --plan techpal-plan --runtime "PYTHON|3.9"
   ```
5. **Deploy**:
   ```bash
   az webapp deployment source config-local-git --name techpal-app --resource-group techpal-rg
   git remote add azure <git-url>
   git push azure main
   ```

## 🔧 Production Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-super-secret-key
DEBUG=false
MAX_REQUESTS_PER_MINUTE=60
```

### Database Migration (SQLite to PostgreSQL)

1. **Install PostgreSQL adapter**:
   ```bash
   pip install psycopg2-binary
   ```

2. **Update DATABASE_URL** in environment variables

3. **The app will automatically create tables** on startup

### SSL/HTTPS Configuration

#### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Let's Encrypt (Automatic SSL)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### Health Checks
- **Endpoint**: `/health`
- **Expected Response**: `{"status": "healthy", ...}`
- **Check Interval**: 30 seconds

### Logging Configuration
```python
# Add to app/api.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('techpal.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring
- **Response Time**: Monitor `/health` endpoint
- **Error Rate**: Check logs for 5xx errors
- **Token Usage**: Track LLM API costs
- **Database**: Monitor connection pool and query performance

## 🔒 Security Checklist

- [ ] **Environment Variables**: All secrets in environment variables
- [ ] **HTTPS**: SSL certificate configured
- [ ] **CORS**: Configured for your domain
- [ ] **Rate Limiting**: Enabled and configured
- [ ] **Input Validation**: All user inputs validated
- [ ] **Content Filtering**: Inappropriate content detection active
- [ ] **Database**: Production database with backups
- [ ] **Monitoring**: Health checks and logging configured

## 🚨 Troubleshooting

### Common Issues

1. **Port Binding Error**:
   ```bash
   # Use environment variable for port
   uvicorn app.api:app --host 0.0.0.0 --port $PORT
   ```

2. **Database Connection Error**:
   - Check DATABASE_URL format
   - Ensure database is accessible
   - Verify credentials

3. **LLM API Errors**:
   - Verify API keys are correct
   - Check API quota/limits
   - Ensure network connectivity

4. **Import Errors**:
   - Check requirements.txt is installed
   - Verify Python version compatibility
   - Check file paths and imports

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=debug

# Run with debug
uvicorn app.api:app --reload --log-level debug
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancer**: Distribute traffic across multiple instances
- **Database**: Use managed PostgreSQL with connection pooling
- **Caching**: Add Redis for session storage
- **CDN**: Serve static assets from CDN

### Vertical Scaling
- **Memory**: Monitor memory usage, increase if needed
- **CPU**: Scale up instance size for high traffic
- **Database**: Upgrade database tier for better performance

### Cost Optimization
- **LLM Provider**: Choose cost-effective models (Claude Haiku vs GPT-4)
- **Caching**: Cache common responses
- **Rate Limiting**: Prevent abuse and reduce costs
- **Monitoring**: Track usage and optimize accordingly

---

**Need Help?** Check the main README.md for more detailed documentation and troubleshooting tips. 