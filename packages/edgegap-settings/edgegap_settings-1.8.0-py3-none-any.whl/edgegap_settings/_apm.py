from pydantic_settings import BaseSettings

from ._configuration import ConsulSettingsConfigDict
from ._fields import ConsulField


class ApmSettings(BaseSettings):
    model_config = ConsulSettingsConfigDict(prefix='APM', frozen=True)
    enabled: bool = ConsulField(key='ENABLED', default=False)
    port: int = ConsulField(key='PORT', default=8200)
    server: str = ConsulField(key='SERVER', default='127.0.0.1')
    token: str = ConsulField(key='TOKEN', default='')
    scheme: str = ConsulField(key='SCHEME', default='http')
