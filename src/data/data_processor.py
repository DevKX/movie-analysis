import pandas as pd

class DataProcessor:

    def __init__(self):
        # Initialize dataframe for movies and ratings
        # Movies data (movieId, title, genres)
        # rating data (userId, movieId, rating, timestamp)
        self.movies_df: pd.DataFrame = pd.DataFrame()
        self.ratings_df: pd.DataFrame = pd.DataFrame()

    def load_data(self, movies_path: str, ratings_path: str) -> None:
        try:
            movies_dtypes = {
                'movieId': 'int32',
                'title': 'string',
                'genres': 'string'
            }
            ratings_dtypes = {
                'userId': 'int32',
                'movieId': 'int32',
                'rating': 'float32'
            }

            # Read CSV
            self.movies_df = pd.read_csv(movies_path, dtype=movies_dtypes)
            self.ratings_df = pd.read_csv(ratings_path, dtype=ratings_dtypes)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading CSVs: {e}")

        # Check for empty datasets
        if self.movies_df.empty or self.ratings_df.empty:
            raise ValueError("Loaded datasets are empty. Please check input files.")

        
        self.movies_df['genres'] = self.movies_df['genres'].astype('category')
        self.ratings_df['timestamp'] = pd.to_datetime(self.ratings_df['timestamp'], unit='s')

        # memory usage info loggin
        print("Movies DF memory usage:", self.movies_df.memory_usage(deep=True).sum() / 1024**2, "MB")
        print("Ratings DF memory usage:", self.ratings_df.memory_usage(deep=True).sum() / 1024**2, "MB") 

    def clean_data(self) -> None:
       
        """
        Clean movies and ratings datasets by removing duplicates and
        handling missing values in key columns.
        """
        # Movies Remove ducplicated movie Id
        self.movies_df.drop_duplicates(subset='movieId', inplace=True)

        # Remove movie where either movie id or title is NaN
        self.movies_df.dropna(subset=['movieId', 'title'], inplace=True)

        # Ratings remove duplicated userId and Movie Id
        self.ratings_df.drop_duplicates(subset=['userId', 'movieId'], inplace=True)

        # Remove rating where any userID or Movie ID and rating is NaN
        self.ratings_df.dropna(subset=['userId', 'movieId', 'rating'], inplace=True)

    

