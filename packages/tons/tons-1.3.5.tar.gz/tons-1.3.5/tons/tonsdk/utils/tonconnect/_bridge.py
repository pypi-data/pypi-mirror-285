import http.client
import json
import time

import requests
from requests import RequestException

from tons.tonsdk.utils.tonconnect.requests_responses._common import BridgeMessage


class Bridge:
    """
    Protocol: https://github.com/ton-blockchain/ton-connect/blob/main/bridge.md
    """

    def __init__(self, bridge_host: str, bridge_port: int, bridge_url: str):
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        self.bridge_url = bridge_url

    def get_event(self, client_id, last_event_id=None, timeout=60) -> (BridgeMessage, int):
        connection = http.client.HTTPSConnection(self.bridge_host, self.bridge_port)
        last_event_id_param = f"&last_event_id={last_event_id}" if last_event_id is not None else ""
        connection.request('GET', f"/bridge/events?client_id={client_id}{last_event_id_param}",
                           headers={'Accept': 'text/event-stream',
                                    'Connection': 'Keep-Alive', })

        start = time.time()
        with connection.getresponse() as response:
            run = True
            while run:
                for line in response:
                    if time.time() - start >= timeout:
                        raise TimeoutError('Timeout while waiting for event.')

                    line = line.decode('UTF-8')
                    if line == '\r\n':
                        run = False
                        break
                    if ':' in line and not line.startswith(':'):
                        key, value = line.split(':', 1)
                        value = value.strip()
                        if key == 'data':
                            data = json.loads(value)
                            run = False
                            break
                        elif key == 'id':
                            event_id = value

        return BridgeMessage.parse_obj(data), int(event_id)

    def send_message(self, client_id, to, data, ttl=300, raise_status_code=True):
        result = requests.post(f'{self.bridge_url}/bridge/message'
                               f'?client_id={client_id}&to={to}&ttl={ttl}', data=data)

        if result.status_code != 200 and raise_status_code:
            raise RequestException(str(result))

        return result
