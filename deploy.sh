#!/bin/bash

# Marketing Campaign Recommendation System - Docker Deployment Script

set -e

echo "🚀 Starting deployment of Marketing Campaign Recommendation System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating template..."
    cat > .env << EOF
# API Keys (Replace with your actual keys)
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=false
EOF
    print_error "Please update the .env file with your actual API keys before continuing."
    exit 1
fi

# Load environment variables
source .env

# Check if required API keys are set
if [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ] || [ -z "$GEMINI_API_KEY" ]; then
    print_error "GEMINI_API_KEY is not set in .env file"
    exit 1
fi

if [ "$GOOGLE_PLACES_API_KEY" = "your_google_places_api_key_here" ] || [ -z "$GOOGLE_PLACES_API_KEY" ]; then
    print_error "GOOGLE_PLACES_API_KEY is not set in .env file"
    exit 1
fi

print_status "Environment variables loaded successfully"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data logs

# Stop existing containers if running
print_status "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Build the Docker image
print_status "Building Docker image..."
docker-compose build --no-cache

# Start the services
print_status "Starting services..."
docker-compose up -d

# Wait for the application to be ready
print_status "Waiting for application to be ready..."
sleep 10

# Check if the application is running
if curl -f http://localhost:3003/ > /dev/null 2>&1; then
    print_status "✅ Application is running successfully!"
    echo ""
    echo "🌐 Application URL: http://localhost:3003"
    echo "📊 Health Check: http://localhost:3003/"
    echo "🎯 API Endpoint: http://localhost:3003/recommend?zipcode=YOUR_ZIPCODE&store_type=YOUR_STORE_TYPE"
    echo ""
    echo "📝 Example API call:"
    echo "curl 'http://localhost:3003/recommend?zipcode=10001&store_type=grocery_store'"
    echo ""
    print_status "📋 To view logs: docker-compose logs -f"
    print_status "🛑 To stop: docker-compose down"
else
    print_error "❌ Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi

print_status "Deployment completed successfully! 🎉" 