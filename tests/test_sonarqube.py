import json
import pytest
from unittest.mock import patch, MagicMock
import requests
from code_explainer.utils.sonarqhube_tool import SonarqubeTool


def _make_tool():
    return SonarqubeTool(
        sonarqube_url="http://sonar.example.com",
        project_key="my-project",
        api_token="secret-token",
    )


# ---------------------------------------------------------------------------
# run() – empty / invalid project key
# ---------------------------------------------------------------------------

def test_run_empty_project_key_returns_empty():
    tool = SonarqubeTool(sonarqube_url="http://sonar.example.com", project_key="", api_token="tok")
    assert tool.run() == ""


@pytest.mark.parametrize("key", ["none", "null", "  "])
def test_run_invalid_project_key_returns_empty(key):
    tool = SonarqubeTool(sonarqube_url="http://sonar.example.com", project_key=key, api_token="tok")
    assert tool.run() == ""


# ---------------------------------------------------------------------------
# run() – happy path
# ---------------------------------------------------------------------------

@patch('code_explainer.utils.sonarqhube_tool.requests.get')
def test_run_returns_json_with_measures(mock_get):
    measures_response = MagicMock()
    measures_response.json.return_value = {
        "component": {
            "measures": [
                {"metric": "bugs", "value": "3"},
                {"metric": "coverage", "value": "78.5"},
            ]
        }
    }
    measures_response.raise_for_status = MagicMock()

    project_response = MagicMock()
    project_response.json.return_value = {"components": [{"key": "my-project", "name": "My Project"}]}
    project_response.raise_for_status = MagicMock()

    mock_get.side_effect = [measures_response, project_response]

    tool = _make_tool()
    result = tool.run()

    data = json.loads(result)
    assert data["measures"]["bugs"] == "3"
    assert data["measures"]["coverage"] == "78.5"
    assert len(data["project_info"]) == 1


@patch('code_explainer.utils.sonarqhube_tool.requests.get')
def test_run_returns_empty_when_no_measures(mock_get):
    measures_response = MagicMock()
    measures_response.json.return_value = {"component": {"measures": []}}
    measures_response.raise_for_status = MagicMock()

    mock_get.return_value = measures_response

    tool = _make_tool()
    result = tool.run()
    assert result == ""


# ---------------------------------------------------------------------------
# run() – error handling
# ---------------------------------------------------------------------------

@patch('code_explainer.utils.sonarqhube_tool.requests.get')
def test_run_returns_empty_on_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("connection refused")
    tool = _make_tool()
    assert tool.run() == ""


@patch('code_explainer.utils.sonarqhube_tool.requests.get')
def test_run_returns_empty_on_invalid_json(mock_get):
    bad_response = MagicMock()
    bad_response.raise_for_status = MagicMock()
    bad_response.json.side_effect = json.JSONDecodeError("err", "", 0)
    mock_get.return_value = bad_response
    tool = _make_tool()
    assert tool.run() == ""


# ---------------------------------------------------------------------------
# Authorization header
# ---------------------------------------------------------------------------

@patch('code_explainer.utils.sonarqhube_tool.requests.get')
def test_run_no_token_no_auth_header(mock_get):
    measures_response = MagicMock()
    measures_response.json.return_value = {"component": {"measures": []}}
    measures_response.raise_for_status = MagicMock()
    mock_get.return_value = measures_response

    tool = SonarqubeTool(sonarqube_url="http://sonar.example.com", project_key="proj", api_token=None)
    tool.run()

    _, call_kwargs = mock_get.call_args
    assert "Authorization" not in call_kwargs.get("headers", {})
