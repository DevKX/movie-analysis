from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from src.data.data_processor import DataProcessor
from src.analysis.data_analysis import DataAnalysis
from src.analysis.data_visualization import DataVisualizer
from src.analysis.data_llm import DataLLM
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
import pandas as pd
import asyncio
import time


# settings for Dashboard report
from datetime import datetime
num_top_movie = 10 # To set number of top movie and number of Rating Time Series
current_year = datetime.now().year
current_month = datetime.now().month
start_year = current_year - 10 # Display rating time series for last 10 years. Due to dated data, we have to drag the period longer to have significant trend
end_year = current_year
end_month = current_month
start_month = current_month

app = FastAPI(title="Movie Data Analysis API")

# Initialize DataProcessor
dp = DataProcessor()


LAST_RELOAD = time.time()
RELOAD_INTERVAL = 3600 # 1 hour

async def background_reloader():
    # Background task that reloads data periodically
    global LAST_RELOAD, dp
    while True:
        await asyncio.sleep(RELOAD_INTERVAL)
        try:
            print(f"♻️ Auto reloading data at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            dp.load_data("data/movies.csv", "data/ratings.csv")
            dp.clean_data()
            LAST_RELOAD = time.time()
        except Exception as e:
            print("⚠️ Error reloading data:", e)


@app.on_event("startup")
async def startup_event():
    # Start background data reload task
    asyncio.create_task(background_reloader())
    dp.load_data("data/movies.csv", "data/ratings.csv")
    dp.clean_data()


class FilterRequest(BaseModel):
    min_ratings: Optional[int] = 0


@app.get("/stats/summary")
def get_statistics():
    # Return aggregated dataset statistics
    try:
        # Instantiate DataAnalysis with the current DataProcessor
        # DataAnalysis holds a reference to dp (self.dp = dp)
        analysis = DataAnalysis(dp)
        stats = analysis.aggregate_statistics(last_reload=LAST_RELOAD) # pass last reload time
        return jsonable_encoder(stats)
    except Exception as e:
        print("ERROR in /stats/summary:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/export")
def export_stats():
    # Export stats as CSV and stream to browser
    try:
        analysis = DataAnalysis(dp)
        stats = analysis.aggregate_statistics(last_reload=LAST_RELOAD)
        df = pd.DataFrame([stats])

        # Write CSV to in-memory buffer
        buf = BytesIO()
        df.to_csv(buf, index=False)
        buf.seek(0)

        # Streaming response to browser
        return StreamingResponse(
            buf,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=movie_stats.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/movies/filter")
def filter_movies(
    min_ratings: int = Query(0, ge=0),
    max_ratings: Optional[int] = Query(None, ge=0),
    genres: Optional[List[str]] = Query(None)):

    try:
        analysis = DataAnalysis(dp)
        filtered = analysis.filter_movies(
            min_ratings=min_ratings,
            max_ratings=max_ratings,
            genres=genres
        )
        return filtered[['movieId', 'title', 'genres']].to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/movies/top")
def get_top_movies(
    limit: int = Query(5, ge=1),     
    min_count_ratings: int = Query(10, ge=0)
):
    try:
        analysis = DataAnalysis(dp)
        top_movies = analysis.get_top_movies(limit=limit, min_count_ratings=min_count_ratings)
        return top_movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/stats")
def get_user_statistics(user_id: int):

    try:
        analysis = DataAnalysis(dp)
        user_stats = analysis.get_user_statistics(user_id=user_id)

        if not user_stats:
            raise HTTPException(status_code=404, detail=f"No ratings found for user ID {user_id}")

        return jsonable_encoder(user_stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts/genres")
def get_genre_chart(min_ratings: int = 0):
    try:
        analysis = DataAnalysis(dp)
        # Get pre-aggregated genre stats
        genre_data = analysis.analyze_genre_trends()
        genre_df = pd.DataFrame(genre_data)

        # Optional filter by minimum total number of ratings
        if min_ratings > 0:
            genre_df = genre_df[genre_df['num_ratings'] >= min_ratings]

        visualizer = DataVisualizer()
        buf = visualizer.plot_genre_popularity(genre_df)

        # Return as image
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts/ratings")
def get_rating_distribution():
    
    # Generate and return the rating distribution histogram as PNG. 
    try:
        analysis = DataAnalysis(dp)
        ratings_df = analysis.dp.ratings_df  # Access current ratings data

        visualizer = DataVisualizer()
        buf = visualizer.create_rating_distribution(ratings_df)

        return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/charts/ratings-time-series")
def get_ratings_time_series_chart(
    movie_id: int = Query(1, ge=1),
    start_year: int = Query(1999 , ge=1900),
    start_month: int = Query(1 , ge=1, le=12),
    end_year: int = Query(2001 , ge=1900),
    end_month: int = Query(12 , ge=1, le=12)
):
    try:
        start_period = pd.Period(f"{start_year}-{start_month:02d}", freq='M')
        end_period = pd.Period(f"{end_year}-{end_month:02d}", freq='M')

        analysis = DataAnalysis(dp)
        ts_data = analysis.generate_time_series_analysis(movie_id=movie_id ,start_period=start_period, end_period=end_period)
        ts_df = pd.DataFrame(ts_data)
        movie_name = analysis.get_movie_name_by_movie_id(movie_id=movie_id)
        if ts_df.empty:
            raise HTTPException(status_code=404, detail="No rating data in the specified range.")

        visualizer = DataVisualizer()
        buf = visualizer.plot_ratings_time_series(ts_df, movie_name)

        return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/recommendations")
def get_movie_recommendation(
    movie_id: int = Query(1 , ge=1),
    num_recommendations: int = Query(5, ge=1)
):
    try:
        analysis = DataAnalysis(dp)
        llm = DataLLM()
        movie_name = analysis.get_movie_name_by_movie_id(movie_id=movie_id)
        
        if movie_name.startswith("Movie "):
            raise HTTPException(status_code=404, detail=f"Movie ID {movie_id} not found")

        return llm.get_movie_recommendation(
            movie_name=movie_name, 
            num_recommendations=num_recommendations
        )

    except HTTPException:
        raise  # Re-raise known HTTP errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {e}")


@app.get("/dashboard/report")
def get_dashboard_report(
    num_top_movies: int = Query(10, ge=1, le=50),
    years_back: int = Query(10, ge=1, le=50)
):
    """
    Generate a full dashboard report HTML with:
    - Summary statistics
    - Top movies with minimum rating count of 50
    - Genre popularity
    - Time series for top movies over last `years_back` years
    """

    try:
        analysis = DataAnalysis(dp)
        visualizer = DataVisualizer()

        # Aggregate statistics
        summary_stats = analysis.aggregate_statistics(last_reload=LAST_RELOAD)

        # Top movies with minimum rating count of 50
        top_movies = analysis.get_top_movies(limit=num_top_movies, min_count_ratings=50)

        # Genre stats
        genre_stats = analysis.analyze_genre_trends()

        # Generate plots
        rating_dist_buf = visualizer.create_rating_distribution(analysis.dp.ratings_df)
        genre_pop_buf = visualizer.plot_genre_popularity(pd.DataFrame(genre_stats))

        # Compute time range
        now = datetime.now()
        start_period = pd.Period(f"{now.year - years_back}-{now.month:02d}", freq="M")
        end_period = pd.Period(f"{now.year}-{now.month:02d}", freq="M")

        # Generate time series for top movies
        time_series_bufs: Dict[str, BytesIO] = {}
        for movie in top_movies:
            ts_data = analysis.generate_time_series_analysis(
                movie_id=movie['movieId'],
                start_period=start_period,
                end_period=end_period
            )
            ts_df = pd.DataFrame(ts_data)
            if not ts_df.empty:
                buf = visualizer.plot_ratings_time_series(ts_df, movie_name=movie['title'])
                time_series_bufs[movie['title']] = buf

        # Generate HTML dashboard report
        html_report = visualizer.generate_dashboard_report(
            analysis_results={
                "summary_stats": summary_stats,
                "top_movies": top_movies,
                "genre_stats": genre_stats
            },
            rating_dist_buf=rating_dist_buf,
            genre_pop_buf=genre_pop_buf,
            time_series_bufs=time_series_bufs
        )

        # Return HTML as streaming response
        return StreamingResponse(
            BytesIO(html_report.encode("utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": "inline; filename=movie_dashboard.html"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard report: {e}")