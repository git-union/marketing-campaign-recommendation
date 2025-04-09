# Marketing Recommendation API

An API that generates targeted marketing campaign recommendations based on local store data and weather conditions.

## Overview

This application collects data about local businesses and current weather patterns, processes this information using several feature engineering steps, and generates tailored marketing campaign recommendations. The system is designed to help businesses create effective marketing strategies based on environmental factors and competitive landscape.

## Features

- **Location Analysis**: Analyzes business density and types in a given zipcode
- **Sentiment Analysis**: Processes customer reviews to gauge market sentiment
- **Weather Integration**: Considers current and forecasted weather conditions
- **Custom Recommendations**: Generates targeted marketing campaigns with actionable insights
- **Docker Containerization**: Easily deployable in any environment
- **HTTPS Support**: Secure API communication

## Architecture

The application follows a modular architecture:

1. **Data Collection**:
   - Google Places API for business data
   - Open-Meteo API for weather information

2. **Feature Engineering**:
   - Store type classification and density analysis
   - Weather pattern processing
   - Sentiment analysis on customer reviews
   - Temporal feature extraction

3. **Recommendation Engine**:
   - GPT-4o powered campaign generation
   - Context-aware marketing suggestions

## Tech Stack

- **Backend**: Flask/Python
- **Containerization**: Docker
- **Deployment**: AWS Elastic Beanstalk
- **Database**: JSON files (local storage)
- **APIs**: 
  - Google Places API
  - OpenAI GPT-4o API
  - Open-Meteo Weather API

## Local Development

### Prerequisites

- Python 3.9+
- Docker
- API keys for:
  - Google Places API
  - OpenAI API

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd feature-engineering
   ```

2. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Build and run with Docker:
   ```bash
   docker build -t marketing-recommendation-app .
   docker run -p 3000:3000 --env-file .env marketing-recommendation-app
   ```

4. Test the API:
   ```bash
   curl "http://localhost:3000/recommend?zipcode=60201&store_type=grocery_store"
   ```

## Deployment to AWS

### Using Elastic Beanstalk

1. Install AWS CLI and EB CLI:
   ```bash
   pip install awscli awsebcli
   ```

2. Initialize Elastic Beanstalk:
   ```bash
   eb init
   # Select region
   # Create application
   # Select Docker platform
   # Set up SSH (optional)
   ```

3. Create an environment:
   ```bash
   eb create marketing-recommendation-env --elb-type application
   ```

4. Set environment variables:
   ```bash
   eb setenv OPENAI_API_KEY=your_key GOOGLE_API_KEY=your_key
   ```

5. Configure HTTPS:
   - Request an SSL certificate in AWS Certificate Manager
   - Add HTTPS listener to your load balancer on port 443
   - Select your certificate

6. Deploy updates:
   ```bash
   eb deploy
   ```

## API Endpoints

### Health Check
```
GET /
```
Returns the status of the API.

### Generate Marketing Recommendations
```
GET /recommend?zipcode={zipcode}&store_type={store_type}
```

Parameters:
- `zipcode`: The ZIP code to analyze
- `store_type`: The type of store (e.g., grocery_store, clothing_store)

Response:
```json
{
  "Insights": [
    "Insight 1: Based on weather information",
    "Insight 2: Based on local competitions",
    "Insight 3: Based on local density",
    "Insight 4: Based on ratings and reviews",
    "Insight 5: Based on consumer behavior and demographics"
  ],
  "Campaigns": [
    {
      "Campaign Title": "Campaign title here",
      "Campaign Description": "Campaign description here",
      "Campaign Duration": "Campaign duration with dates",
      "Discount/Promo": "Discount or promotional offer"
    },
    {
      "Campaign Title": "Second campaign title here",
      "Campaign Description": "Second campaign description here",
      "Campaign Duration": "Second campaign duration with dates",
      "Discount/Promo": "Second discount or promotional offer"
    }
  ]
}
```

## Security Considerations

- API keys are stored as environment variables
- HTTPS is enabled for secure data transmission
- Rate limiting is recommended for production deployments
- Input validation is performed on all parameters

## Further Development

- Add user authentication
- Implement caching for API responses
- Create a web interface for campaign management
- Enhance the recommendation engine with additional data sources
- Add multi-region support for global deployment
