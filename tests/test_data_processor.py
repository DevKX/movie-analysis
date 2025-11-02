import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.data.data_processor import DataProcessor


@pytest.fixture
def mock_data_processor():
    # Fixture to provide a DataProcessor with mocked CSV data

    # Sample movies DataFrame
    movies_df = pd.DataFrame([
        {"movieId": 1, "title": "Movie 1", "genres": "Action|Comedy"},
        {"movieId": 1, "title": "Movie 1", "genres": "Action|Comedy"},  # duplicate
        {"movieId": 2, "title": None, "genres": "Drama"},               # missing title
        {"movieId": 3, "title": "Movie 3", "genres": "Sci-Fi"},
    ])
    movies_df['movieId'] = movies_df['movieId'].astype('int32')
    movies_df['title'] = movies_df['title'].astype('string')
    movies_df['genres'] = movies_df['genres'].astype('category')

    ratings_df = pd.DataFrame([
        {"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": pd.Timestamp("2025-01-01")},
        {"userId": 1, "movieId": 1, "rating": 4.5, "timestamp": pd.Timestamp("2025-01-01")},  # duplicate
        {"userId": 2, "movieId": 2, "rating": None, "timestamp": pd.Timestamp("2025-01-02")}, # missing rating
        {"userId": 3, "movieId": 3, "rating": 5.0, "timestamp": pd.Timestamp("2025-01-03")},
    ])
    ratings_df['userId'] = ratings_df['userId'].astype('int32')
    ratings_df['movieId'] = ratings_df['movieId'].astype('int32')
    ratings_df['rating'] = ratings_df['rating'].astype('float32')
    ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'])

    dp = DataProcessor()
    # Patch pandas.read_csv to return our mocked DataFrames
    with patch("pandas.read_csv") as mock_read_csv:
        mock_read_csv.side_effect = [movies_df.copy(), ratings_df.copy()]
        dp.load_data("fake_movies.csv", "fake_ratings.csv")
        dp.clean_data()
    
    return dp


def test_load_data_empty_csv():
    dp = DataProcessor()
    # Mock pd.read_csv to return empty DataFrames
    with patch("pandas.read_csv", side_effect=[pd.DataFrame(), pd.DataFrame()]):
        with pytest.raises(ValueError) as exc_info:
            dp.load_data("movies.csv", "ratings.csv")
        
        assert "Loaded datasets are empty" in str(exc_info.value)

def test_load_data(mock_data_processor):
    dp = mock_data_processor
    # Check that movies_df and ratings_df are DataFrames and not empty
    assert isinstance(dp.movies_df, pd.DataFrame)
    assert not dp.movies_df.empty
    assert isinstance(dp.ratings_df, pd.DataFrame)
    assert not dp.ratings_df.empty

    # Check columns
    assert "movieId" in dp.movies_df.columns
    assert "title" in dp.movies_df.columns
    assert "genres" in dp.movies_df.columns
    assert "userId" in dp.ratings_df.columns
    assert "movieId" in dp.ratings_df.columns
    assert "rating" in dp.ratings_df.columns
    assert "timestamp" in dp.ratings_df.columns


def test_clean_data_no_duplicates(mock_data_processor):
    dp = mock_data_processor
    assert dp.movies_df['movieId'].duplicated().sum() == 0
    assert dp.ratings_df.duplicated(subset=['userId', 'movieId']).sum() == 0


def test_clean_data_no_missing_values(mock_data_processor):
    dp = mock_data_processor
    assert dp.movies_df[['movieId', 'title']].isnull().sum().sum() == 0
    assert dp.ratings_df[['userId', 'movieId', 'rating']].isnull().sum().sum() == 0


def test_memory_optimization(mock_data_processor):
    dp = mock_data_processor
    assert dp.movies_df['movieId'].dtype == 'int32'
    assert dp.movies_df['title'].dtype.name == 'string'
    assert dp.movies_df['genres'].dtype.name == 'category'
    assert dp.ratings_df['userId'].dtype == 'int32'
    assert dp.ratings_df['movieId'].dtype == 'int32'
    assert dp.ratings_df['rating'].dtype == 'float32'
    assert pd.api.types.is_datetime64_any_dtype(dp.ratings_df['timestamp'])