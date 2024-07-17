# coding=utf-8
import base64
import hashlib
import io
import json
import re
from typing import Any, TypeVar

from .consts import REQUEST_ID_LENGTH

T = TypeVar('T')


def ignore_docs(method: T) -> T:
    """Mark that a method's documentation should not be rendered. Functionally, this decorator is a noop."""
    return method


@ignore_docs
def json_dumps(obj: Any) -> str:
    """Dump JSON to a string with the correct settings and serializer."""
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def _unique_key_to_request_id(unique_key: str) -> str:
    """Generate request ID based on unique key in a deterministic way."""
    id = re.sub(r'([+/=])', '', base64.b64encode(hashlib.sha256(unique_key.encode('utf-8')).digest()).decode('utf-8'))

    return id[:REQUEST_ID_LENGTH] if len(id) > REQUEST_ID_LENGTH else id


def _maybe_parse_body(body: bytes, content_type: str) -> Any:
    if is_content_type_json(content_type):
        return json.loads(body.decode('utf-8'))  # Returns any
    elif is_content_type_xml(content_type) or is_content_type_text(content_type):
        return body.decode('utf-8')
    return body


def is_content_type_json(content_type: str) -> bool:
    """Check if the given content type is JSON."""
    return bool(re.search(r'^application/json', content_type, flags=re.IGNORECASE))


def is_content_type_xml(content_type: str) -> bool:
    """Check if the given content type is XML."""
    return bool(re.search(r'^application/.*xml$', content_type, flags=re.IGNORECASE))


def is_content_type_text(content_type: str) -> bool:
    """Check if the given content type is text."""
    return bool(re.search(r'^text/', content_type, flags=re.IGNORECASE))


def is_file_or_bytes(value: Any) -> bool:
    """Check if the input value is a file-like object or bytes.

    The check for IOBase is not ideal, it would be better to use duck typing,
    but then the check would be super complex, judging from how the 'requests' library does it.
    This way should be good enough for the vast majority of use cases, if it causes issues, we can improve it later.
    """
    return isinstance(value, (bytes, bytearray, io.IOBase))
