"""
"  _____                         _______ ______
" |     |_.-----.-----.--------.|   |   |   __ \
" |       |  _  |  _  |        ||       |      <
" |_______|_____|_____|__|__|__||___|___|___|__|
"
"        Copyright (C) 2023 LoomHR, Inc.
"             All rights reserved.
"""
import datetime
import json
import logging
import os
import threading
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional, NamedTuple, Any, Union

from locked_dict.locked_dict import LockedDict

PayloadPart = dict[Any, Any]
Storage = dict[Any, Any]


class Request(NamedTuple):
    """
    Represents a request with command, ID, timestamp, payload, and optional storage.
    """
    req_cmd: str
    req_id: str
    req_tstamp: datetime
    payload: list[PayloadPart]
    storage: Optional[Storage]

    @classmethod
    def from_json(cls, js: str):
        """
        Creates a Request instance from a JSON string.
        """
        return cls.from_dict(json.loads(js))

    @classmethod
    def from_dict(cls, d: dict[Any, Any]):
        """
        Creates a Request instance from a dictionary.
        """
        return cls(d['req_cmd'], d['req_id'], datetime.fromisoformat(d['req_tstamp']), d['payload'], d['storage'])

    def to_json(self) -> str:
        """
        Converts the Request instance to a JSON string.
        """
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[Any, Any]:
        """
        Converts the Request instance to a dictionary.
        """
        return {
            'req_cmd': self.req_cmd,
            'req_id': self.req_id,
            'req_tstamp': _iso_format(self.req_tstamp),
            'payload': self.payload,
            'storage': self.storage
        }


class Response(NamedTuple):
    """
    Represents a response with ID, timestamp, optional payload, and optional storage.
    """
    resp_id: str
    resp_tstamp: datetime
    payload: Optional[list[PayloadPart]]
    storage: Optional[Storage]

    @classmethod
    def from_json(cls, js: str):
        """
        Creates a Response instance from a JSON string.
        """
        return cls.from_dict(json.loads(js))

    @classmethod
    def from_dict(cls, d: dict[Any, Any]):
        """
        Creates a Response instance from a dictionary.
        """
        return cls(
            d['resp_id'], datetime.fromisoformat(d['resp_tstamp']), _get_opt(d, 'payload'), _get_opt(d, 'storage')
        )

    def to_json(self) -> str:
        """
        Converts the Response instance to a JSON string.
        """
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[Any, Any]:
        """
        Converts the Response instance to a dictionary.
        """
        d = {
            'resp_id': self.resp_id,
            'resp_tstamp': _iso_format(self.resp_tstamp),
            'payload': self.payload,
            'storage': self.storage
        }

        if self.payload is not None:
            d['payload'] = self.payload
        if self.storage is not None:
            d['storage'] = self.storage

        return d


logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
_logger = logging.getLogger('loomhr.sdk')


class LoomHRSpecialist(ABC):
    """
    Abstract base class for a LoomHR specialist.
    """

    @abstractmethod
    def post_request(self, req: Request) -> Optional[Response]:
        """
        Abstract method to post a request and optionally return a response.
        """
        pass


class RequestPayloadPart(NamedTuple):
    """
    Represents a part of the request payload with command, ID, timestamp, and payload part.
    """
    req_cmd: str
    req_id: str
    req_tstamp: datetime
    payload_part: PayloadPart


ResponsePayloadPart = Union[list[PayloadPart], PayloadPart, None]


class LoomHRSpecialistAsyncAdapter(LoomHRSpecialist, ABC):
    """
    Asynchronous adapter for LoomHR specialist using a thread pool executor.
    """

    def __init__(self, pool_size: Optional[int] = None):
        super().__init__()
        self._pool = ThreadPoolExecutor(max_workers=pool_size if pool_size else os.cpu_count())
        self._payloads_parts: list[PayloadPart] = []
        self._lock = threading.Lock()
        self._storage: LockedDict | None = None

    def close(self):
        """
        Shuts down the thread pool.
        """
        self._pool.shutdown()

    @staticmethod
    def make_id() -> str:
        """
        Generates a unique ID.
        """
        return str(uuid.uuid4().hex)

    def post_request(self, req: Request) -> Optional[Response]:
        """
        Posts a request asynchronously, processing payload parts and returning a response.
        """
        if self._storage is None:
            self._storage = LockedDict()
            self._storage.update(req.storage)

        def fn():
            try:
                res: list[PayloadPart] = []
                if req.payload:
                    for p in req.payload:
                        pp = self.execute(RequestPayloadPart(req.req_cmd, req.req_id, req.req_tstamp, p), self._storage)

                        if pp is not None:
                            if not isinstance(pp, list):
                                pp = [pp]

                            parts = list(filter(lambda el: el, pp)) if pp else None

                            if parts:
                                res.extend(parts)
                    with self._lock:
                        if res:
                            self._payloads_parts.extend(res)
            except Exception as e:
                _logger.error(f'Error during processing [error={e}]', exc_info=True)

        self._pool.submit(fn)

        with self._lock:
            if not self._payloads_parts and not self._storage:
                return None

            payloads = self._payloads_parts[:]
            self._payloads_parts.clear()

        return Response(
            LoomHRSpecialistAsyncAdapter.make_id(), _utc_now(), (payloads if payloads else None), self._storage.copy()
        )

    @abstractmethod
    def execute(self, req: RequestPayloadPart, storage: Storage) -> ResponsePayloadPart:
        """
        Abstract method to execute a request payload part.
        """
        pass


def _utc_now() -> datetime:
    """
    Returns the current UTC datetime.
    """
    return datetime.utcnow()


def _get_opt(d: dict[str, Any], k: str) -> Optional[Any]:
    """
    Gets an optional value from a dictionary by key.
    """
    return d[k] if k in d else None


def _iso_format(d: datetime) -> str:
    """
    Formats a datetime to ISO format with milliseconds.
    """
    return d.astimezone().isoformat(timespec='milliseconds')
