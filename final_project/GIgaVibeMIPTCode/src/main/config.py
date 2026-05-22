import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


@dataclass
class AppConfig:
    api_key: str
    api_host: str
    model: str
    limit_message: int | None
    limit_characters: int | None
    temperature: float
    system_prompt: str | None


def load_config() -> AppConfig:
    yaml_data = load_yaml_config()
    raw_config = merge_with_env(yaml_data)

    config = AppConfig(
        api_key=get_required_str(raw_config, 'api_key'),
        api_host=get_required_str(raw_config, 'api_host'),
        model=get_required_str(raw_config, 'model'),
        limit_message=get_optional_positive_int(raw_config, 'limit_message'),
        limit_characters=get_optional_positive_int(raw_config, 'limit_characters'),
        temperature=get_temperature(raw_config),
        system_prompt=get_optional_str(raw_config, 'system_prompt'),
    )

    return config


def load_yaml_config() -> dict[str, Any]:
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    config_path = project_root / 'resources' / 'config.yaml'

    if not config_path.exists():
        return {}

    try:
        with open(config_path, encoding='utf-8') as file:
            data = yaml.safe_load(file)

    except yaml.YAMLError as error:
        raise ValueError('Invalid config.yaml') from error

    except OSError as error:
        raise ValueError(f'Could not read config.yaml: {error}') from error

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError('config.yaml must contain mapping')

    return data


def merge_with_env(yaml_data: dict[str, Any]) -> dict[str, Any]:
    result = dict(yaml_data)

    env_mapping = {
        'API_KEY': 'api_key',
        'API_HOST': 'api_host',
        'MODEL': 'model',
        'LIMIT_MESSAGE': 'limit_message',
        'LIMIT_CHARACTERS': 'limit_characters',
        'LIMIT_CHARS': 'limit_characters',
        'TEMPERATURE': 'temperature',
    }

    for env_name, config_name in env_mapping.items():
        env_value = os.environ.get(env_name)

        if env_value is not None:
            result[config_name] = env_value

    return result


def get_required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'Missing required config parameter: {key}')

    return value.strip()


def get_optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)

    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(f'Config parameter {key} must be string')

    return value


def get_optional_positive_int(data: dict[str, Any], key: str) -> int | None:
    value = data.get(key)

    if value is None:
        return None

    try:
        int_value = int(value)

    except (TypeError, ValueError) as error:
        raise ValueError(f'Config parameter {key} must be integer') from error

    if int_value <= 0:
        raise ValueError(f'Config parameter {key} must be positive')

    return int_value


def get_temperature(data: dict[str, Any]) -> float:
    value = data.get('temperature', 0.3)

    try:
        temperature = float(value)

    except (TypeError, ValueError) as error:
        raise ValueError('Config parameter temperature must be float') from error

    if not 0 <= temperature <= 1:
        raise ValueError('Config parameter temperature must be between 0 and 1')

    return temperature
