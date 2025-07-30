# HackRx 6.0 - Deployment Guide

## 🚀 Deployment Platforms

This guide covers deployment on all recommended platforms for the HackRx 6.0 hackathon.

## 📋 Pre-Deployment Checklist

- ✅ API endpoint `/hackrx/run` implemented
- ✅ Bearer token authentication configured
- ✅ JSON request/response format ready
- ✅ HTTPS support enabled
- ✅ Response time optimized (< 30 seconds)
- ✅ Environment variables configured

## 🌐 Platform-Specific Deployment

### 1. **Heroku Deployment**

#### Setup:

```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.7" > runtime.txt

# Initialize git and deploy
git init
git add .
git commit -m "Initial commit"
heroku create your-hackrx-app
heroku config:set OPENAI_API_KEY=your_openai_api_key
heroku config:set PINECONE_API_KEY=your_pinecone_api_key
heroku config:set PINECONE_ENVIRONMENT=your_pinecone_environment
git push heroku main
```

#### Webhook URL:

```
https://your-hackrx-app.herokuapp.com/api/v1/hackrx/run
```

### 2. **Railway Deployment**

#### Setup:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables
railway variables set OPENAI_API_KEY=your_openai_api_key
railway variables set PINECONE_API_KEY=your_pinecone_api_key
railway variables set PINECONE_ENVIRONMENT=your_pinecone_environment
```

#### Webhook URL:

```
https://your-app.railway.app/api/v1/hackrx/run
```

### 3. **Render Deployment**

#### Setup:

1. Connect your GitHub repository
2. Create new Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables in dashboard

#### Webhook URL:

```
https://your-app.onrender.com/api/v1/hackrx/run
```

### 4. **Vercel Deployment**

#### Setup:

```bash
# Install Vercel CLI
npm install -g vercel

# Create vercel.json
cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
EOF

# Deploy
vercel --prod
```

#### Webhook URL:

```
https://your-app.vercel.app/api/v1/hackrx/run
```

### 5. **AWS/GCP/Azure Deployment**

#### AWS (EC2):

```bash
# Launch EC2 instance
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone and setup
git clone <your-repo>
cd hackrx-6.0
pip3 install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/hackrx.service
```

Service file content:

```ini
[Unit]
Description=HackRx 6.0 API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hackrx-6.0
Environment="PATH=/home/ubuntu/hackrx-6.0/venv/bin"
ExecStart=/home/ubuntu/hackrx-6.0/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Webhook URL:

```
https://your-ec2-instance.com/api/v1/hackrx/run
```

### 6. **DigitalOcean App Platform**

#### Setup:

1. Create new App in DigitalOcean
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Configure environment variables

#### Webhook URL:

```
https://your-app.ondigitalocean.app/api/v1/hackrx/run
```

## 🔧 Environment Configuration

### Required Environment Variables:

```bash
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=hackrx-documents
DATABASE_URL=your_database_url
```

### Optional Environment Variables:

```bash
DEBUG=False
LOG_LEVEL=INFO
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=1000
TEMPERATURE=0.1
```

## 🔒 HTTPS Configuration

### Automatic HTTPS (Recommended):

- Heroku, Railway, Render, Vercel provide automatic HTTPS
- DigitalOcean App Platform includes SSL certificates
- AWS/GCP/Azure can use load balancers with SSL termination

### Manual HTTPS Setup:

```bash
# For custom domains, use Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Performance Optimization

### For Production:

```python
# In main.py, update for production
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=4,  # For production
        log_level="info"
    )
```

### Database Optimization:

```python
# Use connection pooling for production
DATABASE_URL = "postgresql://user:pass@host:port/db?sslmode=require"
```

## 🧪 Testing Deployment

### Pre-Submission Test:

```bash
# Test your deployed endpoint
curl -X POST https://your-app.com/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

### Expected Response:

```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment..."
  ]
}
```

## 🚨 Troubleshooting

### Common Issues:

1. **Port Configuration**:

   ```python
   # Use environment PORT variable
   port = int(os.environ.get("PORT", 8000))
   ```

2. **Database Connection**:

   ```python
   # Use SSL for production databases
   DATABASE_URL = "postgresql://user:pass@host:port/db?sslmode=require"
   ```

3. **Memory Issues**:

   ```python
   # Optimize chunk size for memory constraints
   CHUNK_SIZE = 500  # Reduce if memory limited
   ```

4. **Timeout Issues**:
   ```python
   # Increase timeout for large documents
   TIMEOUT = 60  # seconds
   ```

## 📝 Submission Checklist

Before submitting your webhook URL:

- ✅ API responds within 30 seconds
- ✅ HTTPS is enabled
- ✅ Bearer token authentication works
- ✅ JSON response format is correct
- ✅ Handles the sample document URL
- ✅ Processes all 10 sample questions
- ✅ Returns accurate answers

## 🎯 Final Webhook URL Format

Your submission URL should be:

```
https://your-deployed-app.com/api/v1/hackrx/run
```

## 📞 Support

If you encounter issues:

1. Check platform-specific logs
2. Verify environment variables
3. Test locally first
4. Use the test_demo.py script to validate

---

**Ready for HackRx 6.0 Submission! 🚀**
