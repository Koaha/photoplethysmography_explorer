# 🚀 Deployment Guide

## Render.com Deployment

This guide will walk you through deploying your PPG Analysis Tool to Render.com.

### Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **GitHub Integration**: Connect your GitHub account to Render

### Step 1: Connect GitHub to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub account if not already connected
4. Select your `Photoplethymogram` repository

### Step 2: Configure the Service

Render will automatically detect your `render.yaml` file. The configuration includes:

- **Service Type**: Web Service
- **Name**: ppg-analysis-tool
- **Runtime**: Python 3.11
- **Plan**: Starter (free tier)
- **Build Command**: `pip install -r requirements-prod.txt`
- **Start Command**: `python main-prod.py`
- **Health Check**: `/health` endpoint
- **Auto-deploy**: Enabled (deploys on every push to main branch)

### Step 3: Environment Variables

The following environment variables are automatically set:

- `PYTHON_VERSION`: 3.11.0
- `PORT`: 8080
- `DEBUG`: false
- `PYTHONPATH`: . (current directory)

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build your application
   - Start the service
   - Provide a public URL

### Step 5: Monitor Deployment

- **Build Logs**: Check the build process for any errors
- **Runtime Logs**: Monitor application logs for issues
- **Health Check**: Verify `/health` endpoint returns `{"status": "healthy"}`

### Step 6: Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain and configure DNS

### Troubleshooting

#### Common Issues

1. **Build Failures**:
   - Check `requirements-prod.txt` for dependency conflicts
   - Verify Python version compatibility
   - Check build logs for specific error messages

2. **Runtime Errors**:
   - Check application logs
   - Verify environment variables
   - Test locally with `python main-prod.py`

3. **Health Check Failures**:
   - Ensure `/health` endpoint is working
   - Check if the app is binding to the correct port
   - Verify the app starts without errors

#### Performance Optimization

1. **Enable Caching**: Render automatically caches builds
2. **Optimize Dependencies**: Use specific versions in requirements
3. **Monitor Scaling**: Adjust min/max instances based on traffic

### Environment-Specific Configurations

#### Development
```bash
DEBUG=true
PORT=5000
```

#### Production (Render)
```bash
DEBUG=false
PORT=8080
```

### Security Considerations

1. **Environment Variables**: Never commit secrets to version control
2. **Health Checks**: Use the `/health` endpoint for load balancer health checks
3. **HTTPS**: Render automatically provides SSL certificates
4. **Access Control**: Consider adding authentication if needed

### Monitoring and Logs

1. **Application Logs**: Available in Render dashboard
2. **Build Logs**: Check for dependency and build issues
3. **Performance Metrics**: Monitor response times and resource usage
4. **Error Tracking**: Set up error monitoring for production issues

### Continuous Deployment

With `autoDeploy: true` in your `render.yaml`:
- Every push to `main` branch triggers automatic deployment
- Builds are cached for faster deployments
- Zero-downtime deployments are supported

### Cost Optimization

1. **Starter Plan**: Free tier with limitations
2. **Scaling**: Adjust min/max instances based on usage
3. **Resource Usage**: Monitor memory and CPU usage
4. **Idle Timeout**: Free tier services sleep after 15 minutes of inactivity

### Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Community**: [Render Community](https://community.render.com)
- **Status Page**: [status.render.com](https://status.render.com)

---

## 🐳 Docker Deployment (Alternative)

If you prefer Docker deployment, you can also use the included `Dockerfile.prod`:

```bash
# Build the image
docker build -f Dockerfile.prod -t ppg-analysis-tool .

# Run the container
docker run -p 8080:8080 -e PORT=8080 ppg-analysis-tool
```

## ☁️ Other Cloud Platforms

This application is also configured for:
- **Google Cloud Platform** (GCP)
- **AWS Elastic Beanstalk**
- **Heroku** (with Procfile)
- **DigitalOcean App Platform**
