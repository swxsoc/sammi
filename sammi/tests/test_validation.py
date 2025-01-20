from pathlib import Path
import requests
import requests_mock

import pytest

from sammi.validation import CDFValidator


@pytest.fixture()
def validator():
    """Initialize CDFValidator with default properties."""
    validator = CDFValidator()
    return validator


def test_validate_raw_valid_cdf(validator: CDFValidator):
    """Test validation of raw data."""
    test_data_dir = Path(__file__).parent / "test_data"

    result = validator.validate_raw(test_data_dir / "test_valid.cdf")
    assert type(result) == str
    assert "The following variables are not ISTP-compliant" not in result


def test_validate_raw_invalid_cdf(validator: CDFValidator):
    """Test validation of raw data."""
    test_data_dir = Path(__file__).parent / "test_data"

    result = validator.validate_raw(test_data_dir / "test_invalid.cdf")
    assert type(result) == str
    assert "Global errors" in result
    assert "The following variables are not ISTP-compliant" in result


def test_validate_raw_no_internet(validator: CDFValidator):
    """Test validation when there is no internet connection."""
    test_data_dir = Path(__file__).parent / "test_data"

    with requests_mock.Mocker() as m:
        m.post(validator.api_url, exc=requests.ConnectionError)
        result = validator.validate_raw(test_data_dir / "test_valid.cdf")
        assert "API request failed" in result


def test_validate_raw_server_error(validator: CDFValidator):
    """Test validation when the server returns an error."""
    test_data_dir = Path(__file__).parent / "test_data"

    with requests_mock.Mocker() as m:
        m.post(validator.api_url, status_code=500, text="Internal Server Error")
        result = validator.validate_raw(test_data_dir / "test_valid.cdf")
        assert "API request failed" in result


def test_validate_valid_cdf(validator: CDFValidator):
    """Test validation of a valid CDF file."""
    test_data_dir = Path(__file__).parent / "test_data"

    result = validator.validate(test_data_dir / "test_valid.cdf")
    assert isinstance(result, list)
    assert len(result) == 0


def test_validate_invalid_cdf(validator: CDFValidator):
    """Test validation of an invalid CDF file."""
    test_data_dir = Path(__file__).parent / "test_data"

    result = validator.validate(test_data_dir / "test_invalid.cdf")
    assert isinstance(result, list)
    assert len(result) > 0


def test_validate_no_internet(validator: CDFValidator):
    """Test validation when there is no internet connection."""
    test_data_dir = Path(__file__).parent / "test_data"

    with requests_mock.Mocker() as m:
        m.post(validator.api_url, exc=requests.ConnectionError)
        result = validator.validate(test_data_dir / "test_valid.cdf")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "API request failed" in result[0]


def test_validate_server_error(validator: CDFValidator):
    """Test validation when the server returns an error."""
    test_data_dir = Path(__file__).parent / "test_data"

    with requests_mock.Mocker() as m:
        m.post(validator.api_url, status_code=500, text="Internal Server Error")
        result = validator.validate(test_data_dir / "test_valid.cdf")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "API request failed" in result[0]
