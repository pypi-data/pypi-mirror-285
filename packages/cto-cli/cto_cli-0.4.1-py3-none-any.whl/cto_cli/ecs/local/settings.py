from __future__ import annotations

import os
import json
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from cto_cli.utils.errors import print_error
from json.decoder import JSONDecodeError

CTO_DIR = Path.home() / '.cto'
ECS_SETTINGS_LOCATION = CTO_DIR / 'ecs_settings.json'


class SettingsNotFound(Exception):
    pass


class EnvSettingsNotFound(Exception):
    pass


@dataclass(frozen=True)
class ECSSettings:
    url: str
    token: str
    ecs_path: str
    repo_name: None | str = None
    saas_token: None | str = None

    @classmethod
    def load_from_env(cls) -> ECSSettings:
        try:
            return cls(
                url=os.environ['ECS_URL'],
                token=os.environ['ECS_TOKEN'],
                ecs_path=os.environ['ECS_LOCAL_PATH'],
                saas_token=os.getenv('ECS_SAAS_TOKEN'),
                repo_name=os.getenv('ECS_REPO_NAME'),
            )
        except KeyError:
            raise EnvSettingsNotFound


def load_ecs_settings() -> ECSSettings:
    try:
        return ECSSettings.load_from_env()
    except EnvSettingsNotFound:
        pass

    try:
        with open(ECS_SETTINGS_LOCATION, 'r') as f:
            try:
                return ECSSettings(**json.load(f))
            except JSONDecodeError:
                print_error('Your ECS settings file is corrupted', exit=True)
    except FileNotFoundError:
        raise SettingsNotFound


def get_ecs_path() -> Path:
    try:
        return Path(load_ecs_settings().ecs_path)
    except SettingsNotFound:
        print_error('Please run [b]cto ecs init[/b] first', exit=True)


def get_repo_path() -> Path:
    return get_ecs_path() / 'repo'


def get_hashes_path() -> Path:
    return get_ecs_path() / '.hashes'


try:
    WORKING_DIR = Path.cwd()
except FileNotFoundError:
    print_error(f'Structure has been modified [b]cd {get_repo_path()}[/b]', exit=True)


def check_working_dir_is_empty():
    if any(WORKING_DIR.iterdir()):
        print_error('The current path is not empty', exit=True)


def create_repo_dir() -> None:
    get_repo_path().mkdir(parents=True, exist_ok=True)


def store_settings(url: str, token: str, saas_token: None | str = None, repo_name: None | str = None) -> None:
    CTO_DIR.mkdir(parents=True, exist_ok=True)

    with open(ECS_SETTINGS_LOCATION, 'w') as f:
        f.write(
            json.dumps(
                {
                    'token': token,
                    'url': url,
                    'saas_token': saas_token,
                    'ecs_path': str(WORKING_DIR),
                    'repo_name': repo_name,
                },
                indent=4,
            )
        )


def _validate_workdir_in_ecs_repo_path():
    ecs_repo_path = get_repo_path()

    try:
        WORKING_DIR.relative_to(Path(ecs_repo_path))
    except ValueError:
        print_error(f'Your current working directory is outside your ECS path: [b]{ecs_repo_path}[/b]', exit=True)


def validate_workdir_in_ecs_repo_path(func=None):
    if not func:
        _validate_workdir_in_ecs_repo_path()
        return

    @wraps(func)
    def wrapper(*args, **kwargs):
        _validate_workdir_in_ecs_repo_path()
        return func(*args, **kwargs)

    return wrapper


def get_current_working_dir_relative_path_to_ecs_repo() -> Path:
    ecs_repo_path = get_repo_path()

    try:
        return Path('/') / WORKING_DIR.relative_to(ecs_repo_path)
    except ValueError:
        print_error(f'Your current working directory is outside your ECS repo path: [b]{ecs_repo_path}[/b]', exit=True)
