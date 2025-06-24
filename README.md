# AI-Powered Marketing Campaign Recommendation System

A sophisticated marketing campaign engine that leverages real-time weather data, local market dynamics, and a dual-layer AI to generate strategic, data-driven campaign recommendations for local businesses.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Visit_App-brightgreen?style=for-the-badge)]([https://api.eesita.me](https://api.eesita.me/recommend?zipcode=60201&store_type=flower))

## ✨ Key Features

- **Dynamic Weather Integration**: Ingests 7-day weather forecasts to recommend timely, weather-appropriate promotions.
- **Hyper-Local Market Analysis**: Analyzes local competitor density, customer ratings, and business sentiment to identify market gaps and opportunities.
- **Dual-Layer AI Strategy**:
  1.  **Campaign Generator**: An AI model that creates initial campaign ideas based on a comprehensive feature vector of the market.
  2.  **Marketing Expert AI**: A second AI model that refines, validates, and enhances the initial ideas, ensuring they are realistic, compelling, and effective.
- **RESTful API**: Simple and clean API for generating recommendations on demand.
- **Containerized & Cloud-Ready**: Fully containerized with Docker for easy deployment and architected for scalable deployment on cloud services like AWS ECS.

---

## 🏗️ Architecture Overview

The system follows a data-processing pipeline that culminates in AI-powered analysis:

1.  **Data Fetching**: The `fetch_data` module retrieves store and competitor data from the **Google Places API** and weather forecasts from the **Open-Meteo API**.
2.  **Data Processing & Feature Engineering**: Raw data is cleaned, and key features are extracted. This includes calculating competitor density, aggregating customer ratings, and processing weather data into actionable insights (`src/`).
3.  **Sentiment Analysis**: Customer reviews are analyzed to generate sentiment scores for different store categories.
4.  **AI Recommendation Engine**:
    - A detailed JSON `feature_vector` is constructed, summarizing the entire market context.
    - This vector is fed to the first Gemini AI model to generate initial campaign recommendations.
    - A second, "marketing expert" AI model reviews the initial output, along with raw aggregated data, to improve the campaigns' realism, psychological impact, and competitive edge.
5.  **API Server**: A Flask server exposes the `/recommend` endpoint to deliver the final JSON-formatted recommendations.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured (for AWS deployment).
- Valid API keys for:
  - **Google Cloud Platform** (with Places API enabled)
  - **Google AI Studio** (for Gemini API)

### 1. Environment Setup

Clone the repository and create a `.env` file for your API keys.

```bash
git clone https://github.com/your-username/marketing-campaign-recommendation.git
cd marketing-campaign-recommendation
touch .env
```

Add your API keys to the `.env` file:

```env
# .env
GEMINI_API_KEY="your_gemini_api_key_here"
GOOGLE_PLACES_API_KEY="your_google_places_api_key_here"
```

### 2. Running Locally with Docker

This is the recommended method for local development.

```bash
# Build and run the container in detached mode
docker-compose up --build -d
```

The application will be available at `http://localhost:3000`.

**Other useful commands:**
```bash
# View container logs
docker-compose logs -f

# Check running services
docker-compose ps

# Stop and remove the containers
docker-compose down
```

### 3. Running Natively (Without Docker)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Flask application
python server.py
```

---

## ☁️ Deployment to AWS ECS

This application is designed to be deployed as a container on AWS Elastic Container Service (ECS) with a Fargate launch type.

### Key Deployment Steps

1.  **Build and Push the Docker Image to ECR**:
    - The image must be built for the `linux/amd64` platform to be compatible with AWS Fargate. This is pre-configured in the `docker-compose.yml` file.
    - Create an ECR repository and push the multi-platform image to it.

2.  **Set Up ECS Cluster**:
    - Create a new ECS cluster to host the service.

3.  **Create a Task Definition**:
    - This blueprint defines how to run the container. It specifies the ECR image URI, CPU/memory resources, port mappings, and environment variables.
    - **Crucially**, API keys should be injected securely using **AWS Secrets Manager**, not as plaintext environment variables.

4.  **Create an Application Load Balancer (ALB)**:
    - Set up an ALB and a Target Group to expose the service to the internet.
    - The Target Group's health check should point to the `/` endpoint on the container's port (`3000`).

5.  **Create the ECS Service**:
    - The service launches the task and connects it to the ALB's Target Group.
    - **Critical Networking Configuration**: Ensure the service's Security Group allows inbound traffic on port `3000` from the ALB's Security Group to pass health checks.

---

## 📡 API Documentation

### Health Check

-   `GET /`
-   **Description**: Confirms that the API is running.
-   **Success Response** (`200 OK`):
    ```json
    { "status": "healthy" }
    ```

### Generate Campaign Recommendations

-   `GET /recommend?zipcode={zipcode}&store_type={store_type}`
-   **Description**: Generates marketing campaigns based on the location and store type.
-   **Query Parameters**:
    -   `zipcode` (string, required): The target postal code (e.g., `90210`).
    -   `store_type` (string, required): The type of store (e.g., `grocery_store`, `book_store`).
-   **Example Request**:
    ```bash
    curl "https://api.eesita.me/recommend?zipcode=10001&store_type=clothing_store"
    ```
-   **Example Success Response** (`200 OK`):
    ```json
    {
      "Insights": [
        "Insight 1: With a sunny, warm 7-day forecast, foot traffic is expected to increase.",
        "Insight 2: Local competition is moderate, but customer ratings for competitors are average, indicating an opportunity to capture market share with a superior experience."
      ],
      "Campaigns": [
        {
          "Campaign Title": "Sunshine & Style: Early Summer Showcase",
          "Campaign Description": "The weather is perfect for a wardrobe refresh! Visit us this week to explore our new summer collection. Enjoy a complimentary iced tea while you shop.",
          "Campaign Duration": "June 25, 2024 - July 1, 2024",
          "Discount/Promo": "15% off all new summer arrivals."
        }
      ]
    }
    ```

---

## 📁 Project Structure

```
.
├── src/                  # Core data processing and feature engineering modules
│   ├── cleaning.py
│   ├── feature_extraction.py
│   ├── feature_pipeline.py
│   ├── fetch_data.py
│   ├── sentiment.py
│   └── weather_features.py
├── data/                 # Directory for storing intermediate data files (auto-generated)
├── logs/                 # Directory for storing logs (auto-generated)
├── .dockerignore
├── .gitignore
├── .env                  # Local environment variables (must be created manually)
├── docker-compose.yml    # Docker Compose configuration for local development
├── Dockerfile            # Defines the container image
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── server.py             # Flask API server and main application logic
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
curl https://api.eesita.me/

# Test recommendation
curl "https://api.eesita.me/recommend?zipcode=10001&store_type=grocery_store"
```

## 📊 Monitoring

### Health Checks
- Application health: `https://api.eesita.me/`
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
