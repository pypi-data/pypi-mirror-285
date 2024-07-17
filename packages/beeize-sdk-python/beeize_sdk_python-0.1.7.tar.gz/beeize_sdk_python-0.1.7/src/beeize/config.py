# coding=utf-8
import json
import os
import platform
from typing import Optional, TypeVar, Any

T = TypeVar('T')


class Configuration:
    _default_instance: Optional['Configuration'] = None

    def __init__(self):
        self.base_dir = self._get_base_dir()

    @staticmethod
    def _get_base_dir():
        os_name = platform.system()
        if os_name in ['Windows', 'Darwin']:
            return './storage'
        return '/storage'

    @classmethod
    def _get_default_instance(cls) -> 'Configuration':
        if cls._default_instance is None:
            cls._default_instance = cls()

        return cls._default_instance

    @staticmethod
    def get_config_value(name: str, default: Any = None, parse_json: bool = False) -> Any:
        value = os.getenv(name)
        if value is None:
            return default

        if parse_json:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default

        return value

    @classmethod
    def get_global_configuration(cls) -> 'Configuration':
        return cls._get_default_instance()
