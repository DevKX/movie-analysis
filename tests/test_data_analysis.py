import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.analysis.data_analysis import DataAnalysis

@pytest.fixture
def data_analysis_instance():
    # Fixture to initialize DataAnalysis with mocked DataProcessor

    # Create a mock DataProcessor
    mock_dp = MagicMock()

    # Sample movies dataframe
    mock_dp.movies_df = pd.DataFrame([
        {"movieId": 1, "title": "Movie 1", "genres": "Action|Comedy"},
        {"movieId": 2, "title": "Movie 2", "genres": "Drama"},
    ])

    # Sample ratings dataframe
    mock_dp.ratings_df = pd.DataFrame([
        {"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": pd.Timestamp("2025-01-01")},
        {"userId": 2, "movieId": 1, "rating": 3.5, "timestamp": pd.Timestamp("2025-01-02")},
        {"userId": 1, "movieId": 2, "rating": 5.0, "timestamp": pd.Timestamp("2025-01-03")},
    ])

    return DataAnalysis(mock_dp)


def test_aggregate_statistics(data_analysis_instance):
    stats = data_analysis_instance.aggregate_statistics(last_reload=0)
    expected_keys = [
        "num_movies", "type_of_genres", "num_genres", "num_no_genres",
        "top_genres", "num_ratings", "avg_rating", "min_rating",
        "max_rating", "num_users", "last_reload"
    ]
    for key in expected_keys:
        assert key in stats
    assert isinstance(stats['num_movies'], int)
    assert isinstance(stats['avg_rating'], float)


def test_get_movie_name_by_movie_id(data_analysis_instance):
    movie_name = data_analysis_instance.get_movie_name_by_movie_id(1)
    assert isinstance(movie_name, str)
    assert movie_name == "Movie 1"


def test_filter_movies_min_ratings(data_analysis_instance):
    filtered = data_analysis_instance.filter_movies(min_ratings=1)
    assert isinstance(filtered, pd.DataFrame)
    rating_counts = data_analysis_instance.ratings_df.groupby('movieId')['rating'].count()
    for movie_id in filtered['movieId']:
        assert rating_counts[movie_id] >= 1


def test_get_top_movies_limit_two(data_analysis_instance):
    top_movies = data_analysis_instance.get_top_movies(limit=2, min_count_ratings=0)
    assert len(top_movies) == 2
    for movie in top_movies:
        assert 'movieId' in movie
        assert 'avg_rating' in movie
        assert 'num_ratings' in movie

def test_get_top_movies_limit_one(data_analysis_instance):
    top_movies = data_analysis_instance.get_top_movies(limit=1, min_count_ratings=0)
    assert len(top_movies) == 1
    for movie in top_movies:
        assert 'movieId' in movie
        assert 'avg_rating' in movie
        assert 'num_ratings' in movie

def test_analyze_genre_trends(data_analysis_instance):
    genre_stats = data_analysis_instance.analyze_genre_trends()
    assert isinstance(genre_stats, list)
    if genre_stats:
        sample = genre_stats[0]
        assert 'genres' in sample
        assert 'avg_rating' in sample
        assert 'num_ratings' in sample


def test_get_user_statistics(data_analysis_instance):
    user_stats = data_analysis_instance.get_user_statistics(user_id=1)
    assert 'userId' in user_stats
    assert 'average_rating' in user_stats
    assert 'total_ratings' in user_stats
    assert 'top_rated_movies' in user_stats
    assert isinstance(user_stats['top_rated_movies'], list)


def test_generate_time_series_analysis(data_analysis_instance):
    ts = data_analysis_instance.generate_time_series_analysis(movie_id=1)
    assert isinstance(ts, list)
    if ts:
        sample = ts[0]
        assert 'year_month' in sample
        assert 'avg_rating' in sample
        assert 'num_ratings' in sample