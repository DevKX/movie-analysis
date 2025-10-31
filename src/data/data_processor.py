from typing import Dict, Any
import pandas as pd

class DataProcessor:

    def __init__(self):
        self.movies_df: pd.DataFrame = pd.DataFrame()
        self.ratings_df: pd.DataFrame = pd.DataFrame()

    def load_data(self, movies_path: str, ratings_path: str) -> None:
        """Load movies.csv and ratings.csv"""
        try:
            self.movies_df = pd.read_csv(movies_path)
            self.ratings_df = pd.read_csv(ratings_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e}")

    def clean_data(self) -> None:
        """Remove duplicates and handle missing values"""
        # Movies
        self.movies_df.drop_duplicates(subset='movieId', inplace=True)
        self.movies_df.dropna(subset=['movieId', 'title'], inplace=True)
        # Ratings
        self.ratings_df.drop_duplicates(subset=['userId', 'movieId'], inplace=True)
        self.ratings_df.dropna(subset=['userId', 'movieId', 'rating'], inplace=True)

    def aggregate_statistics(self) -> Dict[str, Any]:
        """Compute basic dataset statistics"""
        stats: Dict[str, Any] = {}

        # Movies stats
        stats['num_movies'] = len(self.movies_df)
        stats['genres'] = self.movies_df['genres'].str.split('|').explode().value_counts().to_dict()

        # Ratings stats
        stats['num_ratings'] = len(self.ratings_df)
        stats['avg_rating'] = self.ratings_df['rating'].mean()
        stats['min_rating'] = self.ratings_df['rating'].min()
        stats['max_rating'] = self.ratings_df['rating'].max()
        stats['ratings_per_movie'] = self.ratings_df.groupby('movieId')['rating'].count().to_dict()

        return stats

    def filter_movies_by_ratings(self, min_ratings: int = 0) -> pd.DataFrame:
        """
        Return movies that have at least `min_ratings` ratings.
        Useful for LLM summaries or top-movie analysis.
        """
        counts = self.ratings_df.groupby('movieId')['rating'].count()
        filtered_movie_ids = counts[counts >= min_ratings].index
        return self.movies_df[self.movies_df['movieId'].isin(filtered_movie_ids)]