from pydantic_settings import SettingsConfigDict


class ConsulSettingsConfigDict(SettingsConfigDict):
    prefix: str
