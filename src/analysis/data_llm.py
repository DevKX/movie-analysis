from groq import Groq
from dotenv import load_dotenv
import os
import json
import json
import re

load_dotenv()  # Reads .env file
API_KEY = os.getenv("GROQ_API_KEY")


# The .env file contains the API key and is not included in GitHub.
# Please request the .env file from the appropriate contact.
# Alternatively, you can generate API key at https://groq.com/
# Place the .env file in /movie-analysis/src
# GROQ_API_KEY=<GROQ API KEY>
client = Groq(api_key=API_KEY)


class DataLLM:
    def __init__(self, model_name: str = "openai/gpt-oss-20b"):
        self.model_name = model_name

    def get_movie_recommendation(
        self, movie_name: str, num_recommendations: int = 5
    ) -> list[dict]:

        # Prompt for better response and return JSON objects
        # provide movie name input and number of recommendations
        prompt = f"""
        You are a movie recommendation assistant.

        Based on the movie "{movie_name}", suggest exactly {num_recommendations} similar movies.

        Return a valid JSON array ONLY. Each item must be a JSON object with keys:
        "title" (string), "genre" (string), "reason" (string).

        Do NOT include quotes around the entire array, extra text, explanations, or Markdown.

        Example:
        [
        {{
            "title": "Movie A",
            "genre": "Action, Adventure",
            "reason": "Because..."
        }},
        {{
            "title": "Movie B",
            "genre": "Comedy, Family",
            "reason": "Because..."
        }}
        ]
        """

        # Get raw LLM response
        raw_response = self.get_completion_from_messages(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7 # Between 0.1 to 1.0: higher = more creative, lower = safer
        )
        try:
            recommended_movies = json.loads(raw_response)
        except json.JSONDecodeError:
            # Use the instance method instead of the class method
            recommended_movies = self.parse_llm_response(raw_response)

        return recommended_movies


    def get_completion_from_messages(self, messages, temperature=0, model: str = None):
        if model is None:
            model = self.model_name  # openai/gpt-oss-20b
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content


    def parse_llm_response(self, raw_response: str):
        try:
            # First attempt: normal JSON load
            result = json.loads(raw_response)
            if isinstance(result, list) and len(result) == 1 and isinstance(result[0], str):
                result = json.loads(result[0])
            return result
        except json.JSONDecodeError:
            cleaned = re.sub(r'\\n', '', raw_response).strip('"')
            try:
                return json.loads(cleaned)
            except Exception:
                return [raw_response]