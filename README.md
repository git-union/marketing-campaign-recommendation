# Marketing Campaign Recommendation System

A sophisticated marketing campaign recommendation system that generates data-driven, weather-aware, and market-optimized campaign suggestions for local businesses using AI-powered analysis.

## 🚀 Features

- **Real-time Weather Integration**: 7-day weather forecast analysis for weather-responsive campaigns
- **Local Market Analysis**: Competitor analysis, spatial density, and customer sentiment
- **AI-Powered Recommendations**: Two-layer Gemini AI system for realistic marketing campaigns
- **Data-Driven Insights**: Comprehensive market and consumer behavior analysis
- **Docker Deployment**: Easy containerized deployment with Docker and Docker Compose

## 🏗️ Architecture

### Two-Layer AI System
1. **Initial Campaign Generation**: Creates base recommendations using market data
2. **Marketing Expert Validation**: Senior marketing expert AI analyzes and improves campaigns for realism and effectiveness

### Data Pipeline
- **Google Places API**: Store data and competitor analysis
- **Open-Meteo API**: Weather forecast and climate data
- **Gemini AI**: Campaign generation and optimization
- **Data Processing**: Feature extraction, sentiment analysis, and market metrics

## 🐳 Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- Valid API keys for Gemini and Google Places

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd marketing-campaign-recommendation
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Deploy using the automated script**
   ```bash
   ./deploy.sh
   ```

### Manual Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Check application status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

3. **Stop the application**
   ```bash
   docker-compose down
   ```

## 🔧 Configuration

### Environment Variables (.env)
```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=false
```

### API Keys Required
- **Gemini API Key**: For AI-powered campaign generation
- **Google Places API Key**: For store and competitor data

## 📡 API Documentation

### Health Check
```http
GET /
```
**Response**: `{"status": "healthy"}`

### Campaign Recommendation
```http
GET /recommend?zipcode={zipcode}&store_type={store_type}
```

#### Parameters
- `zipcode` (required): Target location zipcode
- `store_type` (required): Type of store (e.g., `grocery_store`, `clothing_store`, `book_store`)

#### Example Request
```bash
curl "http://localhost:3003/recommend?zipcode=10001&store_type=grocery_store"
```

#### Example Response
```json
{
  "Insights": [
    "Insight 1: Based on the 7-day weather forecast showing rain this weekend...",
    "Insight 2: Local competition analysis reveals 15 grocery stores...",
    "Insight 3: Spatial density analysis shows high concentration...",
    "Insight 4: Customer sentiment analysis indicates strong satisfaction...",
    "Insight 5: Consumer behavior patterns suggest weekend shopping peaks..."
  ],
  "Campaigns": [
    {
      "Campaign Title": "Weekend Weather Warrior",
      "Campaign Description": "Beat the rain with our indoor shopping experience. Special weekend discounts on comfort foods and essentials.",
      "Campaign Duration": "June 22, 2024 - June 23, 2024",
      "Discount/Promo": "20% off all comfort foods and 10% off essentials"
    }
  ]
}
```

## 🏗️ Project Structure

```
marketing-campaign-recommendation/
├── src/
│   ├── fetch_data.py          # API data fetching
│   ├── cleaning.py            # Data cleaning and normalization
│   ├── feature_extraction.py  # Store data processing
│   ├── weather_features.py    # Weather data processing
│   ├── feature_pipeline.py    # Feature vector building
│   └── sentiment.py           # Sentiment analysis
├── server.py                  # Flask application
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── requirements.txt           # Python dependencies
├── deploy.sh                  # Deployment script
└── README.md                  # This file
```

## 🔍 Data Sources

### Weather Data (Open-Meteo API)
- 7-day daily forecast
- Temperature (max/min)
- Precipitation
- Weather codes
- Humidity and wind data

### Store Data (Google Places API)
- Competitor store locations
- Customer ratings
- Store categories
- Geographic coordinates
- Business information

### AI Analysis (Gemini API)
- Campaign generation
- Market insights
- Consumer psychology
- Competitive analysis

## 🛠️ Development

### Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_key
export GOOGLE_PLACES_API_KEY=your_key

# Run the application
python server.py
```

### Testing
```bash
# Health check
curl http://localhost:3003/

# Test recommendation
curl "http://localhost:3003/recommend?zipcode=10001&store_type=grocery_store"
```

## 📊 Monitoring

### Health Checks
- Application health: `http://localhost:3003/`
- Docker health check configured
- Logs available via `docker-compose logs -f`

### Data Storage
- Intermediate data saved to `./data/` directory
- Logs stored in `./logs/` directory
- Data persisted via Docker volumes

## 🔒 Security

- API keys stored as environment variables
- No sensitive data in codebase
- Production-ready configuration
- Health checks and error handling

## 🚀 Scaling

### Horizontal Scaling
```bash
# Scale to multiple instances
docker-compose up -d --scale marketing-campaign-app=3
```

### Load Balancing
- Add nginx reverse proxy
- Configure load balancer
- Implement caching layer

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the logs: `docker-compose logs -f`
- Verify API keys are correctly set
- Ensure all dependencies are installed
- Check network connectivity for API calls
