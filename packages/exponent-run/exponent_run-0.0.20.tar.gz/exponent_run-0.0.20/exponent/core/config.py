import enum
import json
import logging
import os
from functools import lru_cache
from importlib.metadata import Distribution, PackageNotFoundError
from typing import Any

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

logger = logging.getLogger(__name__)

# If the package is editable, we want to use:
# base_url = localhost:3000
# base_api_url = localhost:8000


def is_editable_install() -> bool:
    if os.getenv("ENVIRONMENT") == "test":
        # We should explicitly set these variables
        # in test when needed
        return False

    try:
        dist = Distribution.from_name("exponent-run")
    except PackageNotFoundError:
        logger.info("No distribution info found for exponent-run")
        return False

    direct_url = dist.read_text("direct_url.json")
    if not direct_url:
        return False

    try:
        direct_url_json = json.loads(direct_url)
    except json.JSONDecodeError:
        logger.warning("Failed to decode distribution info for exponent-run")
        return False

    pkg_is_editable = direct_url_json.get("dir_info", {}).get("editable", False)
    return bool(pkg_is_editable)


class ExponentCloudConfig(BaseModel):
    repo_name: str
    repo_specific_setup_commands: list[str]
    gh_token: str
    runloop_api_key: str


class Environment(str, enum.Enum):
    development = "development"
    staging = "staging"
    production = "production"


class APIKeys(BaseModel):
    development: str | None = None
    staging: str | None = None
    production: str | None = None


SETTINGS_FOLDER = os.path.expanduser("~/.config/exponent")
SETTINGS_FILE_PATH = os.path.join(SETTINGS_FOLDER, "config.json")


class Settings(BaseSettings):
    environment: Environment
    base_url: str
    base_api_url: str

    exponent_api_key: str | None = None
    extra_exponent_api_keys: dict[str, str] = {}
    log_level: str = "WARNING"

    model_config = SettingsConfigDict(
        json_file=SETTINGS_FILE_PATH,
        json_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(  # noqa: PLR0913
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return env_settings, JsonConfigSettingsSource(settings_cls), init_settings

    def write_settings_to_config_file(self) -> None:
        os.makedirs(SETTINGS_FOLDER, exist_ok=True)
        with open(SETTINGS_FILE_PATH, "w") as f:
            f.write(self.model_dump_json(include=self.config_file_keys))

    def get_config_file_settings(self) -> dict[str, Any]:
        return self.model_dump(include=self.config_file_keys)

    @property
    def config_file_path(self) -> str:
        return SETTINGS_FILE_PATH

    @property
    def config_file_keys(self) -> set[str]:
        return {"exponent_api_key", "extra_exponent_api_keys"}

    @property
    def api_key(self) -> str | None:
        if self.environment == Environment.development:
            return self.extra_exponent_api_keys.get(Environment.development)
        elif self.environment == Environment.staging:
            return self.extra_exponent_api_keys.get(Environment.staging)
        elif self.environment == Environment.production:
            return self.exponent_api_key
        else:
            raise ValueError(f"Unknown environment: {self.environment}")

    def update_api_key(self, api_key: str) -> None:
        if self.environment == Environment.development:
            self.extra_exponent_api_keys[Environment.development] = api_key
        elif self.environment == Environment.staging:
            self.extra_exponent_api_keys[Environment.staging] = api_key
        elif self.environment == Environment.production:
            self.exponent_api_key = api_key


@lru_cache(maxsize=1)
def get_settings(use_prod: bool = False, use_staging: bool = False) -> Settings:
    if is_editable_install() and not (use_prod or use_staging):
        base_url = "http://localhost:3000"
        base_api_url = "http://localhost:8000"
        environment = Environment.development
    elif use_staging:
        # TODO: Change this to a real staging URL?
        base_url = "https://exponent.run"
        base_api_url = "https://staging-api.exponent.run"
        environment = Environment.staging
    else:
        base_url = "https://exponent.run"
        base_api_url = "https://api.exponent.run"
        environment = Environment.production

    return Settings(
        base_url=base_url, base_api_url=base_api_url, environment=environment
    )
