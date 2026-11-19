from unittest.mock import Mock, patch

import requests

from src.sources.adzuna_job_source import AdzunaJobSource, JobSearchResult


def make_source():
    source = object.__new__(AdzunaJobSource)
    source.locations = ["Hyderabad"]
    source.results_per_search = 10
    source.max_retries = 3
    source.retry_delay = 2
    source.request_interval = 0
    source._last_request_at = None
    source.app_id = "test-id"
    source.app_key = "test-key"
    return source


def make_response(status_code=200, payload=None, headers=None):
    response = Mock()
    response.status_code = status_code
    response.headers = headers or {}
    response.json.return_value = {"results": []} if payload is None else payload
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    return response


@patch("src.sources.adzuna_job_source.requests.get")
def test_successful_search_returns_structured_jobs(mock_get):
    source = make_source()
    mock_get.return_value = make_response()

    with patch.object(source, "_normalize_jobs", return_value=["job"]):
        result = source.search("DevOps Engineer Hyderabad")

    assert isinstance(result, JobSearchResult)
    assert result.success is True
    assert result.jobs == ["job"]
    assert result.error is None
    assert result.query == "DevOps Engineer Hyderabad"
    assert mock_get.call_count == 1


@patch("src.sources.adzuna_job_source.requests.get")
def test_successful_empty_search_is_not_a_failure(mock_get):
    source = make_source()
    mock_get.return_value = make_response(payload={"results": []})

    result = source.search("DevOps Engineer Hyderabad")

    assert result.success is True
    assert result.jobs == []
    assert result.error is None


@patch("src.sources.adzuna_job_source.time.sleep")
@patch("src.sources.adzuna_job_source.requests.get")
def test_retries_http_429(mock_get, mock_sleep):
    source = make_source()
    mock_get.side_effect = [
        make_response(429, headers={"Retry-After": "3"}),
        make_response(200),
    ]

    result = source.search("DevOps Engineer Hyderabad")

    assert result.success is True
    assert result.jobs == []
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(3.0)


@patch("src.sources.adzuna_job_source.time.sleep")
@patch("src.sources.adzuna_job_source.requests.get")
def test_retries_http_503(mock_get, mock_sleep):
    source = make_source()
    mock_get.side_effect = [make_response(503), make_response(200)]

    result = source.search("DevOps Engineer Hyderabad")

    assert result.success is True
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(2)


@patch("src.sources.adzuna_job_source.time.sleep")
@patch("src.sources.adzuna_job_source.requests.get")
def test_does_not_retry_http_401_and_reports_failure(mock_get, mock_sleep):
    source = make_source()
    mock_get.return_value = make_response(401)

    result = source.search("DevOps Engineer Hyderabad")

    assert result.success is False
    assert result.jobs == []
    assert "HTTP request rejected" in result.error
    assert mock_get.call_count == 1
    mock_sleep.assert_not_called()


@patch("src.sources.adzuna_job_source.requests.get")
def test_invalid_json_reports_failure(mock_get):
    source = make_source()
    response = make_response()
    response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = response

    result = source.search("DevOps Engineer Hyderabad")
    assert result.success is False
    assert "Invalid JSON" in result.error


@patch("src.sources.adzuna_job_source.requests.get")
def test_invalid_response_structure_reports_failure(mock_get):
    source = make_source()
    mock_get.return_value = make_response(payload={"unexpected": []})

    result = source.search("DevOps Engineer Hyderabad")
    assert result.success is False
    assert "results list" in result.error


@patch("src.sources.adzuna_job_source.time.sleep")
@patch("src.sources.adzuna_job_source.requests.get")
def test_retries_network_failure_then_succeeds(mock_get, mock_sleep):
    source = make_source()
    mock_get.side_effect = [
        requests.Timeout("Connection timed out"),
        make_response(200),
    ]

    result = source.search("DevOps Engineer Hyderabad")

    assert result.success is True
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(2)


@patch("src.sources.adzuna_job_source.time.sleep")
@patch("src.sources.adzuna_job_source.requests.get")
def test_exhausted_network_retries_report_failure(mock_get, mock_sleep):
    source = make_source()
    mock_get.side_effect = requests.Timeout("Connection timed out")

    result = source.search("DevOps Engineer Hyderabad")

    assert result.success is False
    assert "after 3 attempts" in result.error
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2
