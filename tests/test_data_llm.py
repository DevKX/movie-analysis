import pytest
from unittest.mock import patch, MagicMock
from src.analysis.data_llm import DataLLM

@pytest.fixture
def llm_instance():
    return DataLLM()

def test_get_movie_recommendation_json_parsing(llm_instance):
    fake_response = '[{"title": "Movie A", "genre": "Action", "reason": "Similar style"}]'

    with patch("src.analysis.data_llm.client.chat.completions.create") as mock_create:
        mock_choice = MagicMock()
        mock_choice.message.content = fake_response
        mock_create.return_value.choices = [mock_choice]

        result = llm_instance.get_movie_recommendation("Toy Story", num_recommendations=1)
        assert isinstance(result, list)
        assert result[0]["title"] == "Movie A"
        assert result[0]["genre"] == "Action"

def test_get_movie_recommendation_invalid_json(llm_instance):
    fake_response = "Not a JSON response"

    with patch("src.analysis.data_llm.client.chat.completions.create") as mock_create:
        mock_choice = MagicMock()
        mock_choice.message.content = fake_response
        mock_create.return_value.choices = [mock_choice]

        result = llm_instance.get_movie_recommendation("Toy Story", num_recommendations=1)
        assert isinstance(result, list)
        assert result[0] == fake_response  # fallback returns raw string