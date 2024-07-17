# coding=utf-8
from typing import Optional, Any

from .config import Configuration
from .input import Input
from .storages import Dataset, RequestQueue, KeyValueStore


class Scraper:
    _default_instance: Optional['Scraper'] = None
    config: Configuration

    def __init__(self, config: Optional[Configuration] = None) -> None:
        self.input = Input()
        self.config: Configuration = config or Configuration()
        self.dataset = Dataset(None, config=self.config)
        self.request_queue = RequestQueue(id=None, config=self.config)
        self.key_value_store = KeyValueStore(id=None, config=self.config)

    def push_data(self, data: Any) -> None:
        if not data:
            return
        self.dataset.push_data(data)


if __name__ == '__main__':
    # python -m src.beeize.scraper
    scraper = Scraper()
    """ 存储数据
    scraper.push_data({"key": "dafwew "})
    """

    """ 添加请求"""
    request_queue = scraper.request_queue
    item = request_queue.add_request(
        {"url": "https://github.com/apify/actor-example-python/blob/master/src/main.py"}
    )
    print(item)
    request_queue.mark_request_as_handled(item)


    """ 存储文件
    key_value_store = scraper.key_value_store
    key_value_store.set_value("asas", {"1": 2})
    print(key_value_store.get_value("asas"))
    
    key_value_store = scraper.key_value_store
    key_value_store.set_value(
        "asas",
        open('/Users/zhaoyang/Desktop/beeize/beeize-sdk-python/src/beeize/storages/request_queue.py', 'r').read(),
        'py'
    )
    print(key_value_store.get_value("asas"))
    """

