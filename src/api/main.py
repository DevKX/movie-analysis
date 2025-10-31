from fastapi import FastAPI, HTTPException, Query
from src.data.data_processor import DataProcessor
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Movie Data Analysis API")

# Initialize DataProcessor and load data at startup
dp = DataProcessor()
dp.load_data("data/movies.csv", "data/ratings.csv")
dp.clean_data()


class FilterRequest(BaseModel):
    min_ratings: Optional[int] = 0


@app.get("/stats")
def get_statistics():
    """Return aggregated dataset statistics"""
    try:
        stats = dp.aggregate_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/movies/filter")
def filter_movies(min_ratings: int = Query(0, ge=0)):
    """Return movies with at least min_ratings ratings"""
    try:
        filtered = dp.filter_movies_by_ratings(min_ratings)
        return filtered[['movieId', 'title', 'genres']].to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
