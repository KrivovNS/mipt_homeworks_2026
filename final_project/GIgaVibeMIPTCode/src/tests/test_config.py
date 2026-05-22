import pytest
from pytest import MonkeyPatch

from src.main.config import (
    get_optional_positive_int,
    get_optional_str,
    get_required_str,
    get_temperature,
    merge_with_env,
)


def test_get_required_str_returns_value() -> None:
    data = {
        'api_key': 'test-key',
    }

    assert get_required_str(data, 'api_key') == 'test-key'


def test_get_required_str_strips_spaces() -> None:
    data = {
        'api_key': '  test-key  ',
    }

    assert get_required_str(data, 'api_key') == 'test-key'


def test_get_required_str_raises_for_missing_value() -> None:
    data: dict[str, object] = {}

    with pytest.raises(
        ValueError,
        match='Missing required config parameter',
    ):
        get_required_str(data, 'api_key')


def test_get_optional_str_returns_none() -> None:
    data: dict[str, object] = {}

    assert get_optional_str(data, 'system_prompt') is None


def test_get_optional_str_returns_value() -> None:
    data = {
        'system_prompt': 'hello',
    }

    assert get_optional_str(data,'system_prompt') == 'hello'


def test_get_optional_str_raises() -> None:
    data = {'system_prompt': 123}

    with pytest.raises(ValueError, match='must be string'):
        get_optional_str(data,'system_prompt')


def test_get_optional_positive_int_returns_value() -> None:
    data = {'limit_message': '20'}

    assert (get_optional_positive_int(data,'limit_message') == 20)


def test_get_optional_positive_int_returns_none() -> None:
    data: dict[str, object] = {}

    assert (get_optional_positive_int(data,'limit_message') is None)


def test_get_optional_positive_int_raises_for_bad_type() -> None:
    data = {'limit_message': 'abc'}

    with pytest.raises(ValueError, match='must be integer'):
        get_optional_positive_int(data,'limit_message')


def test_get_optional_positive_int_raises_for_negative() -> None:
    data = {'limit_message': '-5'}

    with pytest.raises(ValueError, match='must be positive'):
        get_optional_positive_int(data,'limit_message')


def test_get_temperature_returns_value() -> None:
    data = {'temperature': '0.5'}

    assert get_temperature(data) == 0.5


def test_get_temperature_uses_default() -> None:
    assert get_temperature({}) == 0.3


def test_get_temperature_raises_for_bad_type() -> None:
    data = {'temperature': 'abc'}

    with pytest.raises(ValueError, match='must be float'):
        get_temperature(data)


def test_get_temperature_raises_for_invalid_range() -> None:
    data = {'temperature': '2'}

    with pytest.raises(
        ValueError, match='between 0 and 1'):
        get_temperature(data)


def test_merge_with_env(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv('API_KEY','env-key')

    result = merge_with_env({'api_key': 'yaml-key'})

    assert result['api_key'] == 'env-key'
