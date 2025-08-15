# Deployment Guide for PPG Analysis Tool

This guide covers deploying the PPG Analysis Tool to various cloud platforms using Docker.

## 🐳 Docker Setup

### Prerequisites
- Docker installed on your system
- Git repository cloned locally

### Quick Start with Docker

1. **Build the Docker image:**
   ```bash
   docker build -f Dockerfile.prod -t ppg-tool:latest .
   ```

2. **Run locally:**
   ```bash
   docker run -d --name ppg-tool -p 8080:8080 ppg-tool:latest
   ```

3. **Access the application:**
   Open http://localhost:8080 in your browser

### Using Docker Compose (Development)

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f ppg-tool
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## 🚀 Render.com Deployment

### Option 1: Using Render Dashboard

1. **Connect your GitHub repository** to Render.com
2. **Create a new Web Service**
3. **Configure the service:**
   - **Build Command:** `pip install -r requirements-prod.txt`
   - **Start Command:** `python main-prod.py`
   - **Environment Variables:**
     - `PYTHON_VERSION`: `3.11.0`
     - `PORT`: `8080`
     - `DEBUG`: `false`

### Option 2: Using Render Blueprint

1. **Install Render CLI:**
   ```bash
   curl -sSL https://render.com/download-cli/install.sh | bash
   ```

2. **Deploy using the blueprint:**
   ```bash
   render blueprint apply
   ```

### Option 3: Using Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh render
```

## ☁️ Google Cloud Platform Deployment

### Prerequisites

1. **Install Google Cloud SDK:**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Ubuntu/Debian
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
   echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   sudo apt-get update && sudo apt-get install google-cloud-sdk
   ```

2. **Authenticate and set project:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Deploy to Cloud Run

1. **Using Cloud Build (Recommended):**
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

2. **Using deployment script:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh gcp
   ```

3. **Manual deployment:**
   ```bash
   # Build and push image
   docker build -f Dockerfile.prod -t gcr.io/YOUR_PROJECT_ID/ppg-tool .
   docker push gcr.io/YOUR_PROJECT_ID/ppg-tool
   
   # Deploy to Cloud Run
   gcloud run deploy ppg-tool \
     --image gcr.io/YOUR_PROJECT_ID/ppg-tool \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080
   ```

## 🔧 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Port to run the application on | `8080` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `PYTHONPATH` | Python path for imports | `/app/src` | No |

## 📊 Health Checks

The application includes a health check endpoint at `/health` that returns a simple status response. This is used by:

- Docker health checks
- Load balancers
- Cloud platforms for monitoring

## 🔒 Security Features

- **Non-root user:** Application runs as non-root user `app`
- **Minimal base image:** Uses Python slim image to reduce attack surface
- **Security headers:** Nginx configuration includes security headers
- **Port binding:** Only binds to necessary ports

## 📈 Scaling

### Render.com
- **Auto-scaling:** Configured to scale from 1-3 instances
- **Target concurrency:** 100 requests per instance
- **Memory utilization:** Scales at 80% memory usage

### Google Cloud Platform
- **Cloud Run:** Automatically scales to zero when not in use
- **Max instances:** Limited to 10 instances
- **Memory:** 512MB per instance
- **CPU:** 1 vCPU per instance

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   lsof -i :8080
   
   # Kill the process
   kill -9 PID
   ```

2. **Docker build fails:**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker build --no-cache -f Dockerfile.prod -t ppg-tool:latest .
   ```

3. **Application won't start:**
   ```bash
   # Check logs
   docker logs ppg-tool
   
   # Check container status
   docker ps -a
   ```

### Logs and Monitoring

1. **View application logs:**
   ```bash
   # Docker
   docker logs -f ppg-tool
   
   # Docker Compose
   docker-compose logs -f ppg-tool
   ```

2. **Check container health:**
   ```bash
   docker inspect ppg-tool | grep Health -A 10
   ```

## 🚀 Performance Optimization

### Docker Optimizations

- **Multi-stage build:** Reduces final image size
- **Layer caching:** Optimizes build times
- **Minimal dependencies:** Only includes production requirements

### Application Optimizations

- **Debug mode disabled:** Production optimizations enabled
- **Hot reload disabled:** Better performance in production
- **Memory management:** Optimized for cloud deployment

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Render.com Documentation](https://render.com/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Dash Deployment Guide](https://dash.plotly.com/deployment)

## 🤝 Support

If you encounter issues during deployment:

1. Check the troubleshooting section above
2. Review the application logs
3. Verify your cloud platform configuration
4. Check the [GitHub Issues](https://github.com/your-username/ppg-analysis-tool/issues) page
