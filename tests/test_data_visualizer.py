import pytest
import pandas as pd
from io import BytesIO
from src.analysis.data_visualization import DataVisualizer

@pytest.fixture
def visualizer():
    return DataVisualizer()

@pytest.fixture
def mock_genre_stats():
    return pd.DataFrame({
        'genres': ['Action', 'Comedy', 'Drama'],
        'avg_rating': [4.5, 3.8, 4.0],
        'num_ratings': [100, 150, 80]
    })

@pytest.fixture
def mock_ratings_df():
    return pd.DataFrame({
        'userId': [1,2,3,4,5],
        'movieId': [101,102,103,104,105],
        'rating': [4.0, 3.5, 5.0, 2.0, 4.5]
    })

@pytest.fixture
def mock_time_series_df():
    return pd.DataFrame({
        'year_month': ['2025-01','2025-02','2025-03'],
        'avg_rating': [3.5, 4.0, 4.2],
        'num_ratings': [10, 15, 12]
    })

def test_plot_genre_popularity(visualizer, mock_genre_stats):
    buf = visualizer.plot_genre_popularity(mock_genre_stats)
    assert isinstance(buf, BytesIO)
    buf.seek(0)
    assert buf.read(8) == b'\x89PNG\r\n\x1a\n'

def test_create_rating_distribution(visualizer, mock_ratings_df):
    buf = visualizer.create_rating_distribution(mock_ratings_df)
    assert isinstance(buf, BytesIO)
    buf.seek(0)
    assert buf.read(8) == b'\x89PNG\r\n\x1a\n'

def test_plot_ratings_time_series(visualizer, mock_time_series_df):
    buf = visualizer.plot_ratings_time_series(mock_time_series_df, movie_name="Test Movie")
    assert isinstance(buf, BytesIO)
    buf.seek(0)
    assert buf.read(8) == b'\x89PNG\r\n\x1a\n'