from pydantic_settings import BaseSettings

from ._configuration import ConsulSettingsConfigDict
from ._fields import ConsulField


class LogStashSettings(BaseSettings):
    model_config = ConsulSettingsConfigDict(prefix='LOGSTASH', frozen=True)
    enabled: bool = ConsulField(key='ENABLED', default=False)
    port: int = ConsulField(key='PORT', default=5044)
    server: str = ConsulField(key='SERVER', default='127.0.0.1')
