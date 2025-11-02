import pandas as pd
import time
from typing import Dict, Any, Optional, List

from src.data.data_processor import DataProcessor

class DataAnalysis:
 
    # set number of top genres for summary statistic
    num_top_genres = 5;

    def __init__(self, dp: DataProcessor):
        # Keep a reference to DataProcessor to access latest data
        self.dp = dp

    # Return the latest movies/rating dataframe from DataProcesssor
    @property
    def movies_df(self):
        return self.dp.movies_df

    @property
    def ratings_df(self):
        return self.dp.ratings_df

    def get_movie_name_by_movie_id(self, movie_id: int) -> str:
        # Get movie name using movie id
        # Used for LLM movie recommendation and display on rating time series chart title display
        movie_row = self.movies_df[self.movies_df['movieId'] == movie_id]
        if not movie_row.empty:
            return movie_row['title'].values[0]
        else:
            # Return movie id if movie name not found
            return f"Movie {movie_id}"

    def aggregate_statistics(self, last_reload: float) -> Dict[str, Any]:
        # Return a Stat dictionary
        stats: Dict[str, Any] = {}

        # Movies stats
        # Duplicated movie id has been removed as part of clean data function during data processing
        stats['num_movies'] = int(len(self.movies_df))
        genres_exploded = self.movies_df['genres'].str.split('|').explode()

        # remove no genres listed
        # Todo: Consider using a predefined list of valid genres to avoid issues with unexpected or malformed genre entries
        valid_genres_exploded = genres_exploded[genres_exploded.str.lower() != "(no genres listed)"]
        
        # Type of genres. Total 19 genres
        stats['type_of_genres'] = sorted(valid_genres_exploded.unique())
        
        # Count of unique genres
        stats['num_genres'] = int(valid_genres_exploded.nunique())

        # Count of movie with no genres
        # Todo: To log genres not in the predefined list of valid genres
        stats['num_no_genres'] = int(self.movies_df['genres'].str.lower().eq("(no genres listed)").sum())
        
        # Top genres
        stats['top_genres'] = valid_genres_exploded.value_counts().head(self.num_top_genres).to_dict()

        # Ratings stats
        stats['num_ratings'] = int(len(self.ratings_df))
        stats['avg_rating'] = float(self.ratings_df['rating'].mean())
        stats['min_rating'] = float(self.ratings_df['rating'].min())
        stats['max_rating'] = float(self.ratings_df['rating'].max())

        # Users stats
        stats['num_users'] = int(self.ratings_df['userId'].nunique())

        # Last Reload stats are being passed in from API layer
        # Reload every 1 hour control at API Layer (RELOAD_INTERVAL)
        stats['last_reload'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_reload))

        return stats

    def filter_movies(
    self,
    min_ratings: int = 0,
    max_ratings: Optional[int] = None,
    genres: Optional[list[str]] = None
    ) -> pd.DataFrame:

        # Start with all movies
        filtered_df = self.movies_df.copy()

        # Filter by rating counts (Min_ratings and max_rating are optional)
        if min_ratings > 0 or max_ratings is not None:
            rating_counts = self.ratings_df.groupby('movieId')['rating'].count()
            if min_ratings > 0:
                rating_counts = rating_counts[rating_counts >= min_ratings]
            if max_ratings is not None:
                rating_counts = rating_counts[rating_counts <= max_ratings]
            filtered_df = filtered_df[filtered_df['movieId'].isin(rating_counts.index)]

        # Filter by genres
        if genres:
            # access genres column
            # Split each genres into list
            # Apply lambda fn to check if any of genres exist in X
            #Todo: Python loop does not scale with as the data set scale. To optimize
            # filtered_df = filtered_df[
            #     filtered_df['genres'].str.split('|').apply(lambda x: any(g in x for g in genres))
            # ]

            # ChatGPT suggest to use panda vectorize operation
            # Convert filter genres to lowercase
            genres_lower = [g.lower() for g in genres]

            # Explode genres but keep a copy of the original genre for returning later
            df_exploded = filtered_df.assign(
                genres_list=filtered_df['genres'].str.split('|')
            ).explode('genres_list')

            # Compare lowercase for filtering
            df_exploded['genres_lower'] = df_exploded['genres_list'].str.lower()

            # Filter using lowercase
            filtered_df = df_exploded[df_exploded['genres_lower'].isin(genres_lower)]

            # Keep only original columns including original 'genres'
            filtered_df = filtered_df.drop(columns=['genres_list', 'genres_lower']).drop_duplicates('movieId')

        return filtered_df

    def get_top_movies(self, limit: int = 10, min_count_ratings: int = 10) -> List[Dict]:

        # Return top limit(User input) movies sorted by number of rating

        movie_stats = self.ratings_df.groupby('movieId').agg(
            avg_rating=('rating', 'mean'),
            num_ratings=('rating', 'count')
        ).reset_index()

        # filter by min_count_ratings (user input)
        movie_stats_filtered = movie_stats[movie_stats['num_ratings'] >= min_count_ratings]

        # Sort by average rating descending
        top_movies_stats_desc = movie_stats_filtered.sort_values('avg_rating', ascending=False).head(limit)

        # Join with movies_df to get titles and genres
        top_movies = top_movies_stats_desc.merge(self.movies_df, on='movieId', how='left')

        # Convert to list of dictionaries for API response
        return top_movies[['movieId', 'title', 'genres', 'avg_rating', 'num_ratings']].to_dict(orient='records')


    def analyze_genre_trends(self) -> Dict[str, Any]:

            # Avoid modifying original movies dataframe
            df = self.dp.movies_df.copy()

            # Left join between movie df(Left) with rating df
            df = df.merge(self.dp.ratings_df, on='movieId', how='left')
            
            # Split genres
            df = df.assign(genres=df['genres'].str.split('|')).explode('genres')
            
            # Group exploded genre by average rating and number of rating in desc order
            genre_stats = df.groupby('genres').agg(
                avg_rating=('rating', 'mean'),
                num_ratings=('rating', 'count')
            ).sort_values('num_ratings', ascending=False).reset_index()

            return genre_stats.to_dict(orient='records')

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:

        # get user rating based on user Id
        user_ratings = self.dp.ratings_df[self.dp.ratings_df['userId'] == user_id]
        if user_ratings.empty:
            return {}

        # Compute average rating given by given user
        avg_rating = float(user_ratings['rating'].mean())

        # Num of rating given by user
        total_ratings = int(len(user_ratings))

        # Top movies (userId, movieId, rating, title, genres) in desc based on rating
        top_movies = user_ratings.merge(self.dp.movies_df, on='movieId', how='left')
        top_movies = top_movies.sort_values('rating', ascending=False)

        return {
            'userId': user_id,
            'average_rating': avg_rating,
            'total_ratings': total_ratings,
            'top_rated_movies': top_movies[['movieId', 'title', 'rating']].to_dict(orient='records')
        }

    def generate_time_series_analysis(
        self,
        movie_id: int,
        start_period: Optional[pd.Period] = None,
        end_period: Optional[pd.Period] = None
    ) -> Dict[str, Any]:
        
        # Generate monthly rating statistics between start_period and end_period for the given movie ID
        
        ts_df = self.dp.ratings_df.copy()
        # Filter by movie_id provided by input
        # putting all movies from data set will cluttering the results and producing meaningless statistics for this specific movie.
        ts_df = ts_df[ts_df['movieId'] == movie_id]

        ts_df['year_month'] = ts_df['timestamp'].dt.to_period('M')

        # Filter by start and end period if provided
        if start_period:
            ts_df = ts_df[ts_df['year_month'] >= start_period]
        if end_period:
            ts_df = ts_df[ts_df['year_month'] <= end_period]

        # monthly_stats (year_month, avg_rating, num_rating)
        monthly_stats = ts_df.groupby('year_month').agg(
            avg_rating=('rating', 'mean'),
            num_ratings=('rating', 'count')
        ).reset_index()

        monthly_stats['year_month'] = monthly_stats['year_month'].astype(str)
        return monthly_stats.to_dict(orient='records')
    

    def export_stats_csv(self, path: str, last_reload: float):
        # Export aggregated statistics to CSV
        stats = self.aggregate_statistics(last_reload)
        pd.DataFrame([stats]).to_csv(path, index=False)