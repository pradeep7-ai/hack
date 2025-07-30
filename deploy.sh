#!/bin/bash

# HackRx 6.0 - Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 HackRx 6.0 - Deployment Script"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy env.example to .env and configure your API keys."
    echo "cp env.example .env"
    exit 1
fi

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first."
        echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Check if git is initialized
    if [ ! -d .git ]; then
        git init
        git add .
        git commit -m "Initial commit for HackRx 6.0"
    fi
    
    # Create Heroku app if not exists
    if [ -z "$HEROKU_APP_NAME" ]; then
        echo "Creating new Heroku app..."
        heroku create
    else
        echo "Using existing Heroku app: $HEROKU_APP_NAME"
        heroku git:remote -a $HEROKU_APP_NAME
    fi
    
    # Set environment variables
    echo "Setting environment variables..."
    source .env
    heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY"
    heroku config:set PINECONE_API_KEY="$PINECONE_API_KEY"
    heroku config:set PINECONE_ENVIRONMENT="$PINECONE_ENVIRONMENT"
    heroku config:set PINECONE_INDEX_NAME="$PINECONE_INDEX_NAME"
    heroku config:set DATABASE_URL="$DATABASE_URL"
    
    # Deploy
    git add .
    git commit -m "Deploy HackRx 6.0"
    git push heroku main
    
    echo "✅ Deployed to Heroku!"
    echo "🌐 Your webhook URL: https://$(heroku info -s | grep web_url | cut -d= -f2)/api/v1/hackrx/run"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Please install it first."
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    # Login to Railway
    railway login
    
    # Initialize Railway project
    railway init
    
    # Set environment variables
    echo "Setting environment variables..."
    source .env
    railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
    railway variables set PINECONE_API_KEY="$PINECONE_API_KEY"
    railway variables set PINECONE_ENVIRONMENT="$PINECONE_ENVIRONMENT"
    railway variables set PINECONE_INDEX_NAME="$PINECONE_INDEX_NAME"
    railway variables set DATABASE_URL="$DATABASE_URL"
    
    # Deploy
    railway up
    
    echo "✅ Deployed to Railway!"
    echo "🌐 Your webhook URL: https://$(railway status | grep URL | awk '{print $2}')/api/v1/hackrx/run"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    echo "⚠️  Render deployment requires manual setup through the web interface."
    echo ""
    echo "📋 Steps to deploy to Render:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Set Build Command: pip install -r requirements.txt"
    echo "5. Set Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "6. Add environment variables from your .env file"
    echo "7. Deploy!"
    echo ""
    echo "🌐 Your webhook URL will be: https://your-app-name.onrender.com/api/v1/hackrx/run"
}

# Function to test deployment
test_deployment() {
    local url=$1
    echo "🧪 Testing deployment at: $url"
    
    # Test the endpoint
    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60" \
        -d '{
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": ["What is the grace period for premium payment?"]
        }' \
        --max-time 30)
    
    if echo "$response" | grep -q "answers"; then
        echo "✅ Deployment test successful!"
        echo "📄 Response: $response"
    else
        echo "❌ Deployment test failed!"
        echo "📄 Response: $response"
    fi
}

# Main menu
echo ""
echo "Choose deployment platform:"
echo "1) Heroku"
echo "2) Railway"
echo "3) Render (manual)"
echo "4) Test existing deployment"
echo "5) Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_heroku
        ;;
    2)
        deploy_railway
        ;;
    3)
        deploy_render
        ;;
    4)
        read -p "Enter your deployment URL: " url
        test_deployment "$url"
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Test your deployment using the test function"
echo "2. Submit your webhook URL to HackRx 6.0 platform"
echo "3. Monitor your application logs"
echo ""
echo "📚 For more information, see DEPLOYMENT_GUIDE.md" 