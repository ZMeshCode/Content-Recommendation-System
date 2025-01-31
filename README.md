# TV Show Recommendation System

A machine learning-powered TV show recommendation system that provides personalized show suggestions based on user preferences and viewing history.

## Features

- TV show data collection from multiple sources (TVMaze, IMDb, TMDb)
- User-based and item-based collaborative filtering using k-NN
- Deep learning-based recommendation system (Phase 2)
- Web interface for rating shows and receiving recommendations
- Synthetic data generation for initial training

## Project Structure

```
.
├── data/                  # Data storage and processing
│   ├── raw/              # Raw data from APIs
│   ├── processed/        # Cleaned and preprocessed data
│   └── synthetic/        # Generated synthetic data
├── models/               # Model implementations
│   ├── knn/             # k-NN based recommendations
│   └── deep_learning/   # Deep learning models (Phase 2)
├── src/                  # Source code
│   ├── data_collection/ # API integration and data fetching
│   ├── preprocessing/   # Data cleaning and transformation
│   └── evaluation/      # Model evaluation metrics
└── web_app/             # Web application
    ├── backend/         # Flask/FastAPI backend
    └── frontend/        # React frontend
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables for API keys:
   ```bash
   export TMDB_API_KEY="your_tmdb_api_key"
   export TVMAZE_API_KEY="your_tvmaze_api_key"
   ```

## Usage

[Coming soon]

## Development Status

- [x] Project setup
- [ ] Data collection implementation
- [ ] Data preprocessing
- [ ] k-NN model implementation
- [ ] Web app development
- [ ] Deep learning model (Phase 2)

