import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import os
from io import BytesIO  
import base64
from typing import Dict, Any


class DataVisualizer:

    def __init__(self, save_dir: str = './plots'):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True) # Create folder ./plots

    def plot_genre_popularity(self, genre_stats: pd.DataFrame) -> io.BytesIO:
        """
        genre_stats: DataFrame with columns ['genres', 'avg_rating', 'num_ratings']
        Returns a BytesIO buffer containing the PNG image.
        """
        plt.figure(figsize=(10, 6)) # 10 * 6 inches
        genre_stats = genre_stats.sort_values('num_ratings', ascending=False) # Sort genre stats DESC
        sns.barplot(data=genre_stats, x='num_ratings', y='genres', palette="viridis") 
        # set X and Y label and title
        plt.xlabel('Number of Ratings')
        plt.ylabel('Genre')
        plt.title('Genre Popularity by Number of Ratings')
        plt.tight_layout() # Ensure nothing overlaps

        return self._save_plot_to_buffer()

    def create_rating_distribution(self, ratings_df: pd.DataFrame) -> io.BytesIO:
        
        # Generate a histogram showing rating distribution and return as BytesIO.
        plt.figure(figsize=(8, 5))
        sns.histplot(ratings_df['rating'], bins=10, kde=True, color="skyblue")
        plt.title('Rating Distribution')
        plt.xlabel('Rating')
        plt.ylabel('Count')
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()

        return self._save_plot_to_buffer()

    def plot_ratings_time_series(self, ts_df: pd.DataFrame, movie_name: str) -> io.BytesIO:

        # Average Movie Ratings Over Time for Movie Name
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=ts_df, x='year_month', y='avg_rating', marker='o', color='blue')
        plt.xticks(rotation=45)
        plt.xlabel("Month")
        plt.ylabel("Average Rating")
        plt.title(f"Average Movie Ratings Over Time for {movie_name}")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()

        return self._save_plot_to_buffer()

    def _save_plot_to_buffer(self) -> io.BytesIO:
        # Helper function to save the current matplotlib figure into a PNG buffer.
        buf = io.BytesIO() # Save in-memory to BytesIO buffer
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf

    def _plot_to_base64(self, buf: BytesIO) -> str:
        """Convert BytesIO PNG to Base64 string for embedding in HTML."""
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    def generate_dashboard_report(
        self,
        analysis_results: Dict[str, Any],
        rating_dist_buf: BytesIO = None,
        genre_pop_buf: BytesIO = None,
        time_series_bufs: Dict[str, BytesIO] = None
    ) -> str:
        """
        Generate a comprehensive HTML dashboard report.

        Parameters:
        - analysis_results: Dict containing statistical summaries, top movies, genre stats, etc.
        - rating_dist_buf: BytesIO buffer of rating distribution plot
        - genre_pop_buf: BytesIO buffer of genre popularity plot
        - time_series_bufs: Dict of movie_name -> BytesIO for ratings time series

        """
        html_parts: List[str] = []
        html_parts.append("<html><head><title>Movie Analysis Dashboard</title></head><body>")
        html_parts.append("<h1>Movie Analysis Dashboard</h1>")

        # Summary statistics
        html_parts.append("<h2>Summary Statistics</h2><ul>")
        for key, value in analysis_results.get("summary_stats", {}).items():
            html_parts.append(f"<li><b>{key}</b>: {value}</li>")
        html_parts.append("</ul>")

        # Top movies
        top_movies: List[Dict[str, Any]] = analysis_results.get("top_movies", [])
        if top_movies:
            html_parts.append("<h2>Top Movies</h2><table border='1'><tr><th>Movie</th><th>Genres</th><th>Avg Rating</th><th>Num Ratings</th></tr>")
            for movie in top_movies:
                html_parts.append(
                    f"<tr><td>{movie['title']}</td><td>{movie['genres']}</td><td>{movie['avg_rating']}</td><td>{movie['num_ratings']}</td></tr>"
                )
            html_parts.append("</table>")

        # Genre trends table
        genre_stats: List[Dict[str, Any]] = analysis_results.get("genre_stats", [])
        if genre_stats:
            html_parts.append("<h2>Genre Trends</h2><table border='1'><tr><th>Genre</th><th>Avg Rating</th><th>Num Ratings</th></tr>")
            for genre in genre_stats:
                html_parts.append(
                    f"<tr><td>{genre['genres']}</td><td>{genre['avg_rating']:.2f}</td><td>{genre['num_ratings']}</td></tr>"
                )
            html_parts.append("</table>")

        # Plots
        if rating_dist_buf:
            html_parts.append("<h2>Rating Distribution</h2>")
            html_parts.append(f"<img src='{self._plot_to_base64(rating_dist_buf)}' width='600'/>")

        if genre_pop_buf:
            html_parts.append("<h2>Genre Popularity</h2>")
            html_parts.append(f"<img src='{self._plot_to_base64(genre_pop_buf)}' width='600'/>")

        if time_series_bufs:
            html_parts.append("<h2>Ratings Time Series</h2>")
            for movie_name, buf in time_series_bufs.items():
                html_parts.append(f"<h3>{movie_name}</h3>")
                html_parts.append(f"<img src='{self._plot_to_base64(buf)}' width='600'/>")

        html_parts.append("</body></html>")
        return "\n".join(html_parts)