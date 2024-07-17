import asyncio
import json
import logging
import traceback

import websockets

from duwi_smarthome_sdk.const.status import Code
from duwi_smarthome_sdk.api.refresh_token import AuthTokenRefresherClient
from duwi_smarthome_sdk.const.const import WS_URL
from duwi_smarthome_sdk.util.sign import md5_encrypt, sha256_base64
from duwi_smarthome_sdk.util.timestamp import current_timestamp

_LOGGER = logging.getLogger(__name__)


class DeviceSynchronizationWS:
    def __init__(self,
                 on_callback: callable,
                 app_key: str,
                 app_secret: str,
                 access_token: str,
                 refresh_token: str,
                 house_no: str,
                 app_version: str,
                 client_version: str,
                 address: str = None,
                 client_model=None
                 ):
        self._on_callback = on_callback
        self._server_uri = WS_URL if address is None else address
        self._app_key = app_key
        self._app_secret = app_secret
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._house_no = house_no
        self._app_version = app_version
        self._client_version = client_version
        self._client_model = client_model
        self._is_over = False
        self._connection = None
        self._is_connecting = False

    async def connect(self):
        _LOGGER.info('connect ws server...')
        self._connection = await websockets.connect(self._server_uri)

    async def send(self, message):
        if self._connection:
            # _LOGGER.info('send message: %s', message)
            await self._connection.send(message)

    async def disconnect(self):
        if self._connection:
            _LOGGER.info('disconnect ws server...')
            self._is_over = True
            await self._connection.close()

    async def reconnect(self):
        _LOGGER.info('Reconnecting WS server...')
        if self._is_over:
            return
        backoff_time = 1  # 设定初始等待时间
        max_backoff_time = 60  # 最大等待时间
        while not self._is_over:
            try:
                self._is_connecting = True
                await self.connect()
                await self.link()
                await self.bind()
                _LOGGER.info('Reconnected successfully.')
                break  # 成功后退出循环
            except Exception as e:
                _LOGGER.error(f'Failed to reconnect: {e}, will retry in {backoff_time}s...')
                await asyncio.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, max_backoff_time)  # 指数退避

    async def listen(self):
        while not self._is_over:
            try:
                await self.process_messages()
            except websockets.exceptions.ConnectionClosedError:
                _LOGGER.info('listen ws connection closed, trying to reconnect...')
                await self.reconnect()
                await asyncio.sleep(5)
            except Exception as e:
                _LOGGER.error(f'An error occurred during listen: {e}')

    async def link(self):
        _LOGGER.info('link...')
        timestamp = current_timestamp()
        client_id = md5_encrypt(timestamp)

        data = {
            "clientID": client_id,
            "appKey": self._app_key,
            "time": str(timestamp),
            "sign": sha256_base64(client_id, self._app_key, timestamp, self._app_secret),
        }
        json_string = json.dumps(data)
        await self.send(
            'LINK|' + json_string
        )

    async def bind(self):
        _LOGGER.info('bind...')
        data = {
            "accessToken": self._access_token,
            "houseNo": self._house_no,
        }
        json_string = json.dumps(data)
        await self.send(
            'BIND|' + json_string
        )

    async def refresh_token(self):
        auth = AuthTokenRefresherClient(
            app_key=self._app_key,
            app_secret=self._app_secret,
            access_token=self._access_token,
            app_version=self._app_version,
            client_version=self._client_version,
            client_model=self._client_model,
        )
        while not self._is_over:
            status, token = await auth.refresh(
                refresh_token=self._refresh_token)
            if status == Code.SUCCESS.value:
                self._access_token = token.access_token
                self._refresh_token = token.refresh_token
            await asyncio.sleep(5 * 24 * 60 * 60)

    async def keep_alive(self):
        _LOGGER.debug("bbb keep alive...")
        while not self._is_over:
            try:
                _LOGGER.debug("keep alive...")
                await self.send('KEEPALIVE')
                await asyncio.sleep(20)
            except websockets.exceptions.ConnectionClosedError:
                _LOGGER.info('keep_alive ws,connection closed, trying to reconnect...')
                await self.reconnect()
            except Exception as e:
                _LOGGER.error(f'An error occurred during keep_alive: {e}')

    async def process_messages(self):
        async for message in self._connection:
            try:
                if message == "KEEPALIVE":
                    continue
                message = str.replace(message, "&excision&", "")
                try:
                    message_data = json.loads(message)
                except json.JSONDecodeError:
                    _LOGGER.error("Failed to parse JSON message: %s", message)
                    return
                namespace = message_data.get("namespace")
                if namespace == "Duwi.RPS.Link":
                    if message_data.get("result", {}).get("code") != "success":
                        _LOGGER.error(f"error message detail: \n{message}")
                        self._is_over = True
                        return

                await self._on_callback(message)
            except Exception as e:
                _LOGGER.error(f"error message detail: \n{traceback.format_exc()}")
