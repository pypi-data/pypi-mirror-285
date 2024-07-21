import threading
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, List, Optional, Callable, Union, Dict

import requests
from gql import Client
from gql.client import SyncClientSession
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode
from pydantic import BaseModel

from tons.config import TonNetworkEnum
from tons.logging_ import tons_logger


class ErrorMsg(BaseModel):
    message: Optional[str] = None
    code: Optional[int] = None


class DAppWrongResult(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return ". ".join([f"{error.message}, Code: {error.code}" for
                          error in self.errors])


class BroadcastQuery(BaseModel):
    boc: str
    timeout: int


class Limiter:
    def __init__(self, period=0.1):
        self.period = period
        self.next_allowed = time.monotonic() + self.period
        self.lock = threading.Lock()

    def sleep(self):
        while self.next_allowed - time.monotonic() >= 0:
            time.sleep(self.period)

    def acquire(self):
        with self.lock:
            self.sleep()
            self.next_allowed = time.monotonic() + self.period


def _exc_is_code(exc: Union[TransportQueryError, DAppWrongResult], code: int) -> bool:
    try:
        for err in exc.errors:
            if _error_code(err) != code:
                return False
    except (AttributeError, TypeError, KeyError):
        return False
    return True


def _exc_is_429(exc: Union[TransportQueryError, DAppWrongResult]) -> bool:
    return _exc_is_code(exc, 429)


def _error_code(error: Union[ErrorMsg, Dict]) -> int:
    try:
        return int(error.code)
    except AttributeError:
        return int(error['code'])


def _retry_on_code_429(count: int):
    def decorator(method: Callable):
        @wraps(method)
        def wrapped_method(self, *args, **kwargs):
            retries = 0
            while True:
                try:
                    return method(self, *args, **kwargs)
                except (TransportQueryError, DAppWrongResult) as exc:
                    if _exc_is_429(exc) and retries < count:
                        retries += 1
                        tons_logger().debug(f'   code 429: retry {retries} ({method.__name__})')
                        continue
                    raise exc
        return wrapped_method
    return decorator


RPS_LIMIT = 10
RETRIES_ON_429 = 10


class DAppClient:
    def __init__(self, graphql_url: str, broadcast_url: str, websocket_url: str, api_key: str):
        self.api_key = api_key
        self.broadcast_url = broadcast_url
        self.websocket_url = websocket_url
        self.graphql_url = graphql_url
        self._limiter = Limiter(1 / RPS_LIMIT)
        # we don't need to specify ssl context, because requests uses it from the box
        self._broadcast_session = requests.Session()
        client = Client(
            fetch_schema_from_transport=False,
            transport=RequestsHTTPTransport(url=self.graphql_url,
                                            headers=self.__headers(is_json=False)))
        client.connect_sync()
        self._query_session = SyncClientSession(client)

    def query(self, queries: List[DocumentNode], ignore_errors=False) -> List[Any]:
        tons_logger().debug(f' dapp query (n={len(queries)}, '
                            f'ignore_errors={int(ignore_errors)})')
        futures = []
        with ThreadPoolExecutor(max_workers=64) as executor:
            for query in queries:
                futures.append(executor.submit(self._query, query, ignore_errors))

        return [future.result() for future in futures]

    def broadcast(self, queries: List[BroadcastQuery], timeout=61, ignore_errors=False) -> List[Any]:
        tons_logger().debug(f' dapp broadcast (n={len(queries)}, '
                            f'timeout={timeout}, '
                            f'ignore_errors={int(ignore_errors)})')
        futures = []
        with ThreadPoolExecutor(max_workers=64) as executor:
            for query in queries:
                futures.append(executor.submit(self._broadcast, query, timeout, ignore_errors))

        return [future.result() for future in futures]

    def _query(self, query: DocumentNode, ignore_errors: bool):
        try:
            return self.__query(query)
        except TransportQueryError as e:
            self.__handle_errors(e.errors, ignore_errors)

    @_retry_on_code_429(count=RETRIES_ON_429)
    def __query(self, query: DocumentNode):
        self._limiter.acquire()
        tons_logger().debug(f'  dapp execute query')  # use these logs to debug requests per second errors
        return self._query_session.execute(query)

    def _broadcast(self, query: BroadcastQuery, timeout: int, ignore_errors: bool):
        try:
            return self.__broadcast(query, timeout, ignore_errors)
        except TransportQueryError as e:
            self.__handle_errors(e.errors, ignore_errors)

    @_retry_on_code_429(count=RETRIES_ON_429)
    def __broadcast(self, query: BroadcastQuery, timeout: int, ignore_errors: bool):
        self._limiter.acquire()
        tons_logger().debug(f'  dapp execute broadcast')  # use these logs to debug requests per second errors
        resp = self._broadcast_session.post(url=self.broadcast_url,
                                            json=query.dict(),
                                            headers=self.__headers(is_json=True),
                                            timeout=timeout)
        return self.__parse_broadcast_response(resp, ignore_errors)

    # def subscription(self, query: DocumentNode, timeout=31):
    #     websockets_transport = WebsocketsTransport(url=self.websocket_url, headers=self.__headers(is_json=False),
    #                                                close_timeout=0, keep_alive_timeout=timeout)
    #     async with Client(transport=websockets_transport, fetch_schema_from_transport=True) as session:
    #         async for result in session.subscribe(query):
    #             yield result

    def __headers(self, is_json):
        headers = {}

        if is_json:
            headers = {
                'Content-Type': 'application/json',
            }

        if self.api_key:
            headers['API-KEY'] = self.api_key

        return headers

    def __parse_broadcast_response(self, resp: requests.Response, ignore_errors):
        try:
            resp = resp.json()
        except requests.JSONDecodeError:
            self.__handle_errors([{"message": resp.reason, "code": resp.status_code}], ignore_errors)
            return None

        if "errors" in resp and resp['errors']:
            if len(resp['errors']) == 1 and 'message' in resp['errors'][0] \
                    and resp['errors'][0]['message'] == 'timeout':
                # transaction may have been sent and may be committed later
                resp['data']['status'] = 0
                return resp['data']

            else:
                return self.__handle_errors(resp['errors'], ignore_errors)

        return resp['data']

    def __handle_errors(self, errors, ignore_errors):
        if not ignore_errors:
            errors = [ErrorMsg.parse_obj(error)
                      for error in errors]
            raise DAppWrongResult(errors)

        return
