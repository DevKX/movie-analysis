import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from src.api.main import app
from io import BytesIO

mocked_png = BytesIO(b'\x89PNG\r\n\x1a\nmockedpngcontent')

@pytest.fixture
def mock_dp():
    # Mock DataProcessor with sample movies and ratings
    dp_mock = MagicMock()
    dp_mock.movies_df = pd.DataFrame([
        {"movieId": 1, "title": "Movie 1", "genres": "Action|Comedy"},
        {"movieId": 2, "title": "Movie 2", "genres": "Drama"},
    ])
    dp_mock.ratings_df = pd.DataFrame([
        {"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": pd.Timestamp("2025-01-01")},
        {"userId": 2, "movieId": 1, "rating": 3.5, "timestamp": pd.Timestamp("2025-01-02")},
        {"userId": 1, "movieId": 2, "rating": 5.0, "timestamp": pd.Timestamp("2025-01-03")},
    ])
    return dp_mock

@pytest.fixture
def client(mock_dp):
    # Patch DataProcessor in main app
    with patch("src.api.main.dp", mock_dp):
        yield TestClient(app)

# ------------------ Happy path tests ------------------

def test_get_statistics(client):
    with patch("src.api.main.DataAnalysis.aggregate_statistics", return_value={"num_movies": 2, "num_ratings": 3, "num_users": 2, "top_genres": {}}): #Replace function with mocked function that return mocked data
        response = client.get("/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert "num_movies" in data
        assert "num_ratings" in data
        assert "num_users" in data
        assert "top_genres" in data

def test_get_top_movies(client):
    with patch("src.api.main.DataAnalysis.get_top_movies", return_value=[{"movieId": 1, "title": "Movie 1", "genres": "Action|Comedy", "avg_rating": 4.5, "num_ratings": 2}]):
        response = client.get("/movies/top?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        for movie in data:
            assert "movieId" in movie
            assert "title" in movie
            assert "avg_rating" in movie
            assert "num_ratings" in movie

def test_get_rating_distribution_chart(client):
    with patch("src.api.main.DataVisualizer.create_rating_distribution", return_value=mocked_png):
        response = client.get("/charts/ratings")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

def test_get_genre_chart(client):
    with patch("src.api.main.DataVisualizer.plot_genre_popularity", return_value=mocked_png):
        response = client.get("/charts/genres")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

def test_get_user_statistics(client):
    with patch("src.api.main.DataAnalysis.get_user_statistics", return_value={"userId": 1, "average_rating": 4.0, "total_ratings": 2, "top_rated_movies": []}):
        response = client.get("/users/1/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == 1
        assert "average_rating" in data
        assert "total_ratings" in data
        assert "top_rated_movies" in data

# ------------------ Unhappy path tests ------------------

def test_get_user_statistics_not_found(client):
    with patch("src.api.main.DataAnalysis.get_user_statistics", return_value={}):
        response = client.get("/users/9999/stats")
        assert response.status_code == 404

def test_get_statistics_exception(client):
    with patch("src.api.main.DataAnalysis.aggregate_statistics", side_effect=Exception("fail")):
        response = client.get("/stats/summary")
        assert response.status_code == 500
        assert "fail" in response.json()["detail"]

def test_get_top_movies_exception(client):
    with patch("src.api.main.DataAnalysis.get_top_movies", side_effect=Exception("fail")):
        response = client.get("/movies/top")
        assert response.status_code == 500

def test_rating_chart_exception(client):
    with patch("src.api.main.DataVisualizer.create_rating_distribution", side_effect=Exception("fail")):
        response = client.get("/charts/ratings")
        assert response.status_code == 500

def test_genre_chart_exception(client):
    with patch("src.api.main.DataVisualizer.plot_genre_popularity", side_effect=Exception("fail")):
        response = client.get("/charts/genres")
        assert response.status_code == 500

def test_time_series_chart_exception(client):
    with patch("src.api.main.DataVisualizer.plot_ratings_time_series", side_effect=Exception("fail")):
        response = client.get("/charts/ratings-time-series?movie_id=1")
        assert response.status_code == 500