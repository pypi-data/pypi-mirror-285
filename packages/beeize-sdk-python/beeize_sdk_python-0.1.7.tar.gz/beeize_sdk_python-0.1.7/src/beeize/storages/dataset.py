# coding=utf-8
import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Union, Optional

from ..config import Configuration

JSONSerializable = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class Dataset:
    _lock = threading.Lock()

    def __init__(self, id: [None, str], config: Configuration):
        self._id = id or config.get_config_value('DATASET_ID', 'default')
        self.config = config
        self.datasets_path = os.path.join(
            self.config.base_dir,
            'datasets',
            self._id
        )
        os.makedirs(self.datasets_path, exist_ok=True)
        self.metadata = self.load_metadata()

    def load_metadata(self):
        metadata_path = os.path.join(self.datasets_path, '__metadata__.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as file:
                return json.load(file)
        return {
            'id': self._id,
            'itemCount': 0,
            'accessedAt': None,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'modifiedAt': None
        }

    def update_metadata(self):
        metadata_path = os.path.join(self.datasets_path, '__metadata__.json')
        with open(metadata_path, 'w', encoding='utf-8', errors='ignore') as file:
            json.dump(self.metadata, file, indent=4, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())

    def push_data(self, data: Any) -> None:
        if not isinstance(data, (dict, list, str, int, float, bool, type(None))):
            raise ValueError("Data is not JSON serializable")

        with self._lock:
            try:
                self.metadata['itemCount'] += 1
                file_name = f"{str(self.metadata['itemCount']).zfill(9)}.json"
                file_path = os.path.join(self.datasets_path, file_name)
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.flush()
                    os.fsync(file.fileno())
                self.metadata['accessedAt'] = datetime.now(timezone.utc).isoformat()
                self.metadata['modifiedAt'] = datetime.now(timezone.utc).isoformat()
                self.update_metadata()  # 保存元数据更改
            except IOError as e:
                print(f"An error occurred: {e}")
