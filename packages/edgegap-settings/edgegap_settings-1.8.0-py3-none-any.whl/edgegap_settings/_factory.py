import logging
import os
import sys
from typing import Any, TypeVar

from dotenv import load_dotenv
from edgegap_consul import ConsulReader, ConsulReaderFactory
from edgegap_logging import DefaultFormatter
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from ._model import SourceValue

load_dotenv()

logger = logging.getLogger('settings.Factory')

# Small Temporary formatting since this is most likely be called before any Logger Initialization
fmt = DefaultFormatter()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(fmt)
logger.addHandler(handler)

T = TypeVar('T', bound=BaseSettings)


class SettingsFactory:
    __mapping__: dict[str, type(BaseSettings)] = {}
    __consul_reader: ConsulReader = ConsulReaderFactory().from_env()

    @classmethod
    def from_settings(cls, settings: type[T]) -> T:
        name = settings.__name__

        if name not in cls.__mapping__.keys():
            consul_prefix = settings.model_config.get('prefix')
            data = {}

            for field_name, field in settings.model_fields.items():
                if isinstance(field.json_schema_extra, dict):
                    consul_key = field.json_schema_extra.get('consul_key')
                    env_key = field.json_schema_extra.get('env_key')
                    value = None

                    # Check if in Environment Variable First
                    if isinstance(env_key, str):
                        value = cls.__from_env(env_key, field.default)

                    # Consul Override Environment Variable
                    if isinstance(consul_prefix, str) and isinstance(consul_key, str):
                        value = cls.__from_consul(f'{consul_prefix}/{consul_key}', field.default)

                    if value is not None:
                        data[field_name] = value

            try:
                cls.__mapping__[name] = settings(**data)
            except ValidationError as e:
                raise ValueError('There was some errors during the Validation of your Settings, please adjust') from e

        return cls.__mapping__.get(name)

    @classmethod
    def __handle_default(cls, from_value: SourceValue) -> Any:
        if from_value.has_value:
            return from_value.value
        elif not from_value.has_value and from_value.has_default:
            if from_value.exists:
                logger.warning(
                    f'Key [{from_value.key}] defined in [{from_value.source}] but the value was None,'
                    f" will fallback to default value '{from_value.default}'",
                )
            else:
                logger.warning(
                    f'Key [{from_value.key}] does not exists in [{from_value.source}] but '
                    f"default is defined to: '{from_value.default}'",
                )
        else:
            raise ValueError(f'Consul key [{from_value.key}] is not defined and no default value')

    @classmethod
    def __from_env(cls, env_key: str, default: Any) -> Any:
        value = os.environ.get(env_key)
        exists = env_key in os.environ.keys()

        from_value = SourceValue(
            key=env_key,
            value=value,
            default=default,
            source='Environment Variables',
            exists=exists,
        )
        return cls.__handle_default(from_value)

    @classmethod
    def __from_consul(cls, consul_full_key: str, default: Any) -> Any:
        exists, value = cls.__consul_reader.get(key=consul_full_key)
        from_value = SourceValue(
            key=consul_full_key,
            value=value,
            default=default,
            source='Consul',
            exists=exists,
        )
        return cls.__handle_default(from_value)

    @classmethod
    def clear(cls):
        cls.__mapping__.clear()
