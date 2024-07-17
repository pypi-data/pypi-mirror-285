# coding=utf-8
import io
import json
import os
import threading
from datetime import datetime, timezone
from typing import Optional, Union, TypeVar

from ..config import Configuration

T = TypeVar('T')


class KeyValueStore:
    _lock = threading.Lock()

    def __init__(self, id: [None, str], config: Configuration):
        self._id = id or config.get_config_value('KV_STORE_ID', 'default')
        self.config = config
        self.kv_store_path = os.path.join(
            self.config.base_dir,
            'kv_stores',
            self._id
        )
        os.makedirs(self.kv_store_path, exist_ok=True)
        self.metadata = self.load_metadata()

    def load_metadata(self):
        metadata_path = os.path.join(self.kv_store_path, '__metadata__.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as file:
                return json.load(file)
        return {
            'id': self._id,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'modifiedAt': datetime.now(timezone.utc).isoformat(),
            'accessedAt': None
        }

    def update_metadata(self, accessed=False):
        now = datetime.now(timezone.utc).isoformat()
        self.metadata['itemCount'] = self.metadata.get('itemCount', 0) + 1
        if accessed:
            self.metadata['accessedAt'] = now
        else:
            self.metadata['modifiedAt'] = now
        with open(os.path.join(self.kv_store_path, '__metadata__.json'), 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(self.metadata, f, indent=4)
            f.flush()
            os.fsync(f.fileno())

    def set_value(self, key: str, value: Union[str, bytes, dict, list], extension: Optional[str] = None) -> None:
        with self._lock:
            extension = extension or self._determine_extension(value)
            content_type = self._determine_content_type(value)
            filename = f'{key}.{extension}'

            data_file_path = os.path.join(self.kv_store_path, filename)
            self._write_data(value, data_file_path, content_type)

            metadata = {
                'key': key,
                'contentType': content_type,
                'extension': extension,
                'filename': filename,
                'size': os.path.getsize(data_file_path),
            }
            file_path = os.path.join(self.kv_store_path, f'{key}.__metadata__.json')
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
            self.update_metadata()

    def get_value(self, key: str) -> Optional[Union[str, bytes, dict, list]]:
        metadata_file_path = os.path.join(self.kv_store_path, f'{key}.__metadata__.json')
        if not os.path.exists(metadata_file_path):
            return None

        with open(metadata_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            metadata = json.load(f)

        data_file_path = os.path.join(self.kv_store_path, metadata['filename'])
        self.update_metadata(accessed=True)
        return self._read_data(data_file_path, metadata['contentType'])

    @staticmethod
    def _determine_extension(value) -> str:
        if isinstance(value, str):
            return 'txt'
        elif isinstance(value, (dict, list)):
            return 'json'
        elif isinstance(value, (bytes, bytearray, io.IOBase)):
            # 字节签名字典
            signatures = {
                b'\xFF\xD8\xFF\xDB': 'jpeg',
                b'\xFF\xD8\xFF\xE0': 'jpeg',
                b'\x89\x50\x4E\x47': 'png',
                b'%PDF-': 'pdf',
                b'\x50\x4B\x03\x04': 'zip',
                b'\x42\x4D': 'bmp',
                b'\x47\x49\x46\x38': 'gif',
                b'\x49\x49\x2A\x00': 'tiff',
                b'\x4D\x4D\x00\x2A': 'tiff',
                b'\x00\x00\x01\x00': 'ico',
                b'\x00\x00\x02\x00': 'cur',
                b'\x52\x61\x72\x21': 'rar',
                b'\xD0\xCF\x11\xE0': 'doc/xls/ppt',
                b'\x25\x50\x44\x46': 'pdf',
                b'\x49\x44\x33': 'mp3',
                b'\x00\x00\x00\x20\x66\x74\x79\x70': 'mp4',
                b'\x1A\x45\xDF\xA3': 'mkv',
                b'\x30\x26\xB2\x75': 'wmv',
                b'\x4F\x67\x67\x53': 'ogg',
                b'\x52\x49\x46\x46': 'avi/wav',
                b'\x66\x4C\x61\x43': 'flac',
            }
            # 检查字节签名
            for signature, format_name in signatures.items():
                if value[:8].startswith(signature):
                    return format_name
        else:
            raise ValueError("Unsupported data type for KeyValueStore")

    @staticmethod
    def _determine_content_type(value) -> str:
        if isinstance(value, str):
            return 'text/plain; charset=utf-8'
        elif isinstance(value, (dict, list)):
            return 'application/json; charset=utf-8'
        elif isinstance(value, (bytes, bytearray, io.IOBase)):
            return 'application/octet-stream'
        else:
            raise ValueError("Unsupported data type for KeyValueStore")

    @staticmethod
    def _write_data(value, file_path: str, content_type: str) -> None:
        if content_type == 'application/json; charset=utf-8':
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                json.dump(value, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
        elif content_type in ['text/plain; charset=utf-8', 'application/octet-stream']:
            mode = 'w' if isinstance(value, str) else 'wb'
            with open(file_path, mode, encoding='utf-8' if mode == 'w' else None) as f:
                f.write(value)
                f.flush()
                os.fsync(f.fileno())

    @staticmethod
    def _read_data(file_path: str, content_type: str) -> Union[str, bytes, dict, list]:
        if content_type == 'application/json; charset=utf-8':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return json.load(f)
        elif content_type == 'text/plain; charset=utf-8':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif content_type == 'application/octet-stream':
            with open(file_path, 'rb') as f:
                return f.read()
