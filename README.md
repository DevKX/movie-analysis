# 🎬 Movie Analysis API

A FastAPI-based application for analyzing movie and rating datasets.  
It provides RESTful endpoints for retrieving statistics, generating visualizations, exploring user trends, and generating dashboard reports — built with Python, FastAPI, Pandas, and Matplotlib.

---

## 🧠 Features

- **Data Analytics** — Aggregates movie, rating, and user statistics  
- **Data Visualization** — Generates genre charts and rating distributions (PNG charts)  
- **Dashboard Reporting** — Full HTML dashboard with stats, top movies, genre popularity, and rating time series  
- **FastAPI Endpoints** — Clean RESTful API  
- **CSV Export** — Export summary statistics as CSV  
- **LLM Movie Recommendations** — LLM-based movie recommendations  
- **Automated Testing** — Comprehensive pytest suite  
- **Modular Architecture** — Separated into data, analysis, and API layers  

---

## 🗂 Project Structure

```plaintext
movie-analysis/
├── data/                     # Input CSV datasets
├── reports/                  # Contains dashboard_report.html
├── src/
│   ├── api/
│   │   └── main.py           # FastAPI routes and app entrypoint
│   ├── data/
│   │   └── data_processor.py # Data loading and cleaning
│   ├── analysis/
│   │   ├── data_analysis.py      # Analytical computations
│   │   ├── data_visualization.py # Chart generation (Matplotlib)
│   │   └── data_llm.py           # AI-based movie recommendations
├── tests/                    # Unit and API tests
├── requirements.txt
├── run.sh                    # Setup and run script
└── README.md
```

---

## ⚙️ Prerequisites

- **Python 3.10+** (tested with 3.12)  
- **macOS/Linux** (Windows users can run via WSL)  
- `pip` installed  

### Environment Setup

If your application requires API keys (e.g., for LLM-based movie recommendations), store them securely in a `.env` file:

1. Generate API key at [https://groq.com](https://groq.com/)  
2. Create `.env` file in `/movie-analysis/src`
3. Add into .env file `GROQ_API_KEY=<YOUR_GROQ_API_KEY>`


### Installation
 1. Clone the Repository (git clone https://github.com/DevKX/movie-analysis.git)
 2. cd movie-analysis
 3. chmod +x run.sh
 4. ./run.sh
    



### run.sh automates the setup and launch of your FastAPI app by:
 1. Creating a Python virtual environment if missing,
 2. Running the FastAPI server, and
 3. Opening the API docs in a browser.



### Running Tests

# Run the unit and API test suite
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing


## Technologies Used

- Python 3.12  
- FastAPI  
- Uvicorn  
- Pandas  
- Matplotlib / Seaborn  
- Pytest  

---

## API Endpoints

All endpoints return JSON (except charts → PNG, dashboard → HTML, export → CSV).

| Endpoint | Method | Query Parameters | Description |
|--------|--------|------------------|-------------|
| `/stats/summary` | `GET` | — | Returns overall dataset statistics (total movies, ratings, users, etc.) |
| `/stats/export` | `GET` | — | Exports aggregated statistics as downloadable `movie_stats.csv` |
| `/movies/top` | `GET` | `limit` (int, default: `5`), `min_count_ratings` (int, default: `10`) | Retrieves top N highest-rated movies with at least `min_count_ratings` |
| `/movies/filter` | `GET` | `min_ratings` (int, default: `0`), `max_ratings` (int, optional), `genres` (list, e.g. `?genres=Action&genres=Comedy`) | Filters movies by number of ratings and genres |
| `/charts/ratings` | `GET` | — | Returns **rating distribution histogram** as PNG |
| `/charts/genres` | `GET` | `min_ratings` (int, default: `0`) | Returns **genre popularity bar chart** (filtered by min total ratings) as PNG |
| `/charts/ratings-time-series` | `GET` | `movie_id` (int, default: `1`), `start_year`, `start_month`, `end_year`, `end_month` | Returns **monthly rating trend** for a specific movie as PNG |
| `/users/{user_id}/stats` | `GET` | Path: `user_id` (int) | Returns user’s rating stats: count, average, min/max, most-rated genre |
| `/movies/recommendations` | `GET` | `movie_id` (int, default: `1`), `num_recommendations` (int, default: `5`) | Returns **AI-generated movie recommendations** using LLM |
| `/dashboard/report` | `GET` | `num_top_movies` (int, default: `10`, max: `50`), `years_back` (int, default: `10`, max: `50`) | Generates **full interactive HTML dashboard** with stats, charts, and top movie trends |

---

### Example Requests

```bash
# Get summary stats
curl http://localhost:8000/stats/summary

# Download stats as CSV
curl http://localhost:8000/stats/export -o movie_stats.csv

# Top 10 movies with at least 100 ratings
curl "http://localhost:8000/movies/top?limit=10&min_count_ratings=100"

# Filter movies in Action & Sci-Fi with at least 50 ratings
curl "http://localhost:8000/movies/filter?min_ratings=50&genres=Action&genres=Sci-Fi"

# Get rating distribution chart
curl http://localhost:8000/charts/ratings --output ratings_chart.png

# Get genre chart (only genres with 1000+ ratings)
curl "http://localhost:8000/charts/genres?min_ratings=1000" --output genres.png

# Rating trend for movie ID 1 from 2000 to 2005
curl "http://localhost:8000/charts/ratings-time-series?movie_id=1&start_year=2000&start_month=1&end_year=2005&end_month=12" --output trend.png

# User stats
curl http://localhost:8000/users/123/stats

# AI recommendations for movie ID 1
curl "http://localhost:8000/movies/recommendations?movie_id=1&num_recommendations=5"

# Full dashboard (top 15 movies, last 5 years)
curl "http://localhost:8000/dashboard/report?num_top_movies=15&years_back=5" --output dashboard.html

```


## Performance Optimizations

- **Memory-efficient dtypes** — `int32`, `float32`, and `category` used for `DataFrame` columns to reduce memory footprint  
- **In-memory chart generation** — All visualizations use `BytesIO` to eliminate disk I/O  
- **Asynchronous data reload** — Background task refreshes datasets every hour without blocking API  
- **Vectorized operations** — Pandas filtering & aggregations avoid slow Python loops for large-scale performance  

---

## Limitations

- **AI Recommendations** — LLM may return malformed JSON; clients should handle raw string fallbacks  
- **Dashboard Generation** — In-memory processing can be slow on very large datasets; limited to top `num_top_movies` and `years_back`  
- **Data Freshness** — Source CSVs are reloaded **every 1 hour**; changes not reflected until next cycle  

---

## AI Tools Used

This project was developed with the assistance of **ChatGPT (GPT-5)** for:

- Structuring modular project layout  
- Code generation & review (with manual validation)  
- Writing comprehensive test cases and improving coverage  
- Edge case analysis and data processing optimization  
- Drafting `README.md` and documentation  

---
