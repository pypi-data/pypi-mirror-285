# coding=utf-8
import json
import os
import threading
from datetime import datetime, timezone
from typing import Dict, Optional

from ..config import Configuration
from ..utils import _unique_key_to_request_id


class RequestQueue:
    def __init__(self, id: [None, str], config: Configuration):
        self._id = id or config.get_config_value('REQUEST_QUEUE_ID', 'default')
        self.config = config
        self._lock = threading.Lock()
        self.request_queues_path = os.path.join(
            self.config.base_dir,
            'request_queues',
            self._id
        )
        os.makedirs(self.request_queues_path, exist_ok=True)
        self._queue = []
        self._requests_cache = {}
        self._handled_count = 0
        self._total_count = 0
        self._last_activity = None
        self.metadata = self.load_metadata()

    def load_metadata(self):
        for filename in os.listdir(self.request_queues_path):
            if filename.endswith('.json') and not filename.startswith('__'):
                with open(os.path.join(self.request_queues_path, filename), 'r', encoding='utf-8', errors='ignore') as f:
                    request = json.load(f)
                    if request.get('status', '') != 'handled':
                        self._queue.append(request)
                    self._requests_cache[request['requestId']] = request

        metadata_path = os.path.join(self.request_queues_path, '__metadata__.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as file:
                metadata = json.load(file)
                self._total_count = metadata.get('totalCount', 0)
                self._handled_count = metadata.get('handledCount', 0)
                return metadata
        return {
            'id': self._id,
            'handledCount': 0,
            'totalCount': 0,
            'accessedAt': None,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'modifiedAt': None
        }

    def update_metadata(self):
        metadata = {
            'id': self._id,
            'handledCount': self._handled_count,
            'totalCount': self._total_count,
            'accessedAt': datetime.now(timezone.utc).isoformat(),
            'createdAt': self._last_activity.isoformat() if self._last_activity else None,
            'modifiedAt': datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(self.request_queues_path, '__metadata__.json'), 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(metadata, f, indent=4)
            f.flush()
            os.fsync(f.fileno())

    def add_request(self, request: Dict, *, forefront: bool = False) -> Dict:
        with self._lock:
            self._last_activity = datetime.now(timezone.utc)
            request_id = request.get('requestId')
            if request.get('uniqueKey') is None:
                request['uniqueKey'] = request['url']

            if not request_id:
                request_id = _unique_key_to_request_id(request['uniqueKey'])
                request['requestId'] = request_id

            if request_id in self._requests_cache:
                return self._requests_cache[request_id]

            self._queue.insert(0, request) if forefront else self._queue.append(request)
            self._requests_cache[request_id] = request
            self._total_count += 1
            with open(os.path.join(self.request_queues_path, f'{request_id}.json'), 'w', encoding='utf-8', errors='ignore') as f:
                json.dump(request, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            self.update_metadata()
            return request

    def get_request(self, request_id: str) -> Optional[Dict]:
        with self._lock:
            return self._requests_cache.get(request_id)

    def fetch_next_request(self) -> Optional[Dict]:
        with self._lock:
            if self._queue:
                self._last_activity = datetime.now(timezone.utc)
                return self._queue.pop(0)
            return None

    def mark_request_as_handled(self, request: Dict):
        with self._lock:
            request_id = request.get('requestId')
            if request_id in self._requests_cache:
                self._requests_cache[request_id]['status'] = 'handled'
                self._handled_count += 1
                with open(os.path.join(self.request_queues_path, f'{request_id}.json'), 'w', encoding='utf-8', errors='ignore') as f:
                    json.dump(self._requests_cache[request_id], f, indent=4)
                    f.flush()
                    os.fsync(f.fileno())
                self.update_metadata()

    def reclaim_request(self, request: Dict):
        with self._lock:
            request_id = request.get('requestId')
            if request_id in self._requests_cache:
                request = self._requests_cache[request_id]
                request['status'] = 'pending'
                self._queue.append(request)

    def is_finished(self) -> bool:
        with self._lock:
            if not self._queue:
                return False
            return True
