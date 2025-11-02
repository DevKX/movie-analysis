Movie Analysis API

A FastAPI-based application for analyzing movie and rating datasets.
It provides RESTful endpoints for retrieving statistics, generating visualizations, exploring user trends, and generating dashboard reports — built with Python, FastAPI, Pandas, and Matplotlib.

⸻

Features
• Data Analytics — Aggregates movie, rating, and user statistics
• Data Visualization — Generates genre charts and rating distributions (PNG charts)
• Dashboard Reporting — Full HTML dashboard with stats, top movies, genre popularity, and rating time series
• FastAPI Endpoints — Clean RESTful API
• CSV Export — Export summary statistics as CSV
• LLM Movie Recommendations — LLM-based movie recommendations
• Automated Testing — Comprehensive pytest suite with >85% coverage
• Modular Architecture — Separated into data, analysis, and API layers

⸻

Project Structure

movie-analysis/
├── data/
├── reports/						# Contain dashboard_report.html
├── src/
│   ├── api/
│   │   └── main.py              	# FastAPI routes and app entrypoint
│   ├── data/
│   │   └── data_processor.py    	# Handles data loading and cleaning
│   ├── analysis/
│   │   ├── data_analysis.py     	# Analytical computations
│   │   ├── data_visualization.py	# Chart generation using Matplotlib
│   │   └── data_llm.py          	# AI-based movie recommendation logic
├── tests/                       	# Unit and API tests
├── requirements.txt
├── run.sh                       	# Script to set up and run the app
└── README.md

⸻

Prerequisites:
• Python 3.10+ (tested with 3.12)
• macOS/Linux (Windows users can run via WSL)
• pip installed
• env Setup



If your application requires API keys (for example, for LLM-based movie recommendations or external services), store them securely in a `.env` file in the project root:

1. Generate API key at https://groq.com/

2. Create a `.env` file in (/movie-analysis/src):
    ```
    # .env
    GROQ_API_KEY=<GROQ API KEY>
    ```
3. Please do not check in your .env


Installation
1) Clone the Repository
git clone https://github.com/DevKX/movie-analysis.git
cd movie-analysis

2) Run the App Automatically
chmod +x run.sh
./run.sh


run.sh automates the setup and launch of your FastAPI app by:
	1.	Creating a Python virtual environment if missing,
	2.	Installing dependencies from requirements.txt,
	3.	Running the FastAPI server, and
	4.	Opening the API docs in a browser.

⸻

Running Tests

Run the unit and API test suite:
pytest -v

Run with coverage report:
pytest --cov=src --cov-report=term-missing

⸻

Technologies Used

• Python 3.12
• FastAPI
• Uvicorn
• Pandas
• Matplotlib / Seaborn
• Pytest

⸻

API Endpoints

Endpoint: /stats/summary
Method: GET
Description: Returns overall dataset statistics

Endpoint: /stats/export
Method: GET
Description: Exports aggregated statistics as CSV

Endpoint: /movies/top?limit=5
Method: GET
Description: Retrieves top N movies by rating

Endpoint: /movies/filter?min_ratings=...&max_ratings=...&genres=...
Method: GET
Description: Returns movies filtered by rating count and genres

Endpoint: /charts/ratings
Method: GET
Description: Returns rating distribution chart (PNG)

Endpoint: /charts/genres
Method: GET
Description: Returns genre popularity chart (PNG)

Endpoint: /charts/ratings-time-series?movie_id=...
Method: GET
Description: Returns rating trends over time for a specific movie (PNG)

Endpoint: /users/{user_id}/stats
Method: GET
Description: Returns user’s movie rating stats

Endpoint: /movies/recommendations?movie_id=...&num_recommendations=N
Method: GET
Description: Returns AI-driven movie recommendations for a given movie

Endpoint: /dashboard/report?num_top_movies=N&years_back=M
Method: GET
Description: Generates full HTML dashboard with statistics, top movies, genre popularity, and rating time series for last M years

⸻

Performance Optimizations

- Optimized `DataFrame` dtypes (`int32`, `float32`, `category`) to reduce memory usage.
- Charts generated in-memory (`BytesIO`) to avoid disk I/O overhead.
- Background task reloads datasets asynchronously to prevent API blocking.
- Utilized pandas vectorization instead of Python loops for filtering and aggregations to improve performance on large datasets.

⸻


Limitations

• AI Movie Recommendations — The LLM-based recommendation engine may occasionally return unexpected or malformed JSON responses. Clients should be prepared to handle raw string fallbacks if JSON parsing fails.
• Dashboard & Reporting — Dashboard generation is performed in-memory and may be slower for very large datasets. Only the top N movies (`num_top_movies`) and a fixed lookback period (`years_back`) are included in the report.
• Data Updates — Data reload occurs periodically via a background task (default: every 1 hour). Changes to the source CSV files may not be immediately reflected in API responses until the next reload cycle.

⸻

AI Tools Used

This project was developed with the assistance of ChatGPT (GPT-5) for:
	• Structuring the project layout
	• Code Generation & Review (With understanding and adjustment before implementation)
	• Writing test cases and improving coverage
	• Reviewing edge cases and optimizing data processing logic
	• Drafting README.md content

⸻
