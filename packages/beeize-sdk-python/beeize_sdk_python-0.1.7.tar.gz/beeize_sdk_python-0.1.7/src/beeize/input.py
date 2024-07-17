# coding=utf-8
import json
import os
import random


class Input:
    @staticmethod
    def get_request_list(name: str) -> list:
        return json.loads(os.getenv(name.upper()))

    @staticmethod
    def get_bool(name: str) -> bool:
        return os.getenv(name.upper(), 'false') == 'true'

    @staticmethod
    def get_int(name: str) -> int:
        return int(os.getenv(name.upper()))

    @staticmethod
    def get_float(name: str) -> float:
        return float(os.getenv(name.upper()))

    @staticmethod
    def get_string(name: str) -> str:
        return os.getenv(name.upper())

    @staticmethod
    def get_list(name: str) -> list:
        try:
            return [i.get('url') for i in json.loads(os.getenv(name.upper()))]
        except (Exception,):
            return json.loads(os.getenv(name.upper()))

    @staticmethod
    def get_dict(name: str) -> dict:
        return json.loads(os.getenv(name.upper()))

    @staticmethod
    def get_proxies():
        proxy_url = os.getenv('proxy_url'.upper())
        if proxy_url:
            return proxy_url.split(',')

    def get_random_proxy(self):
        proxy_list = self.get_proxies()
        if proxy_list:
            return random.choice(proxy_list)

    @staticmethod
    def is_free_user():
        return os.getenv('user_plan'.upper()) == 'FREE'
