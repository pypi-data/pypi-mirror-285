import json
import logging
from typing import Optional

from duwi_smarthome_sdk.util.sign import md5_encrypt
from duwi_smarthome_sdk.util.timestamp import current_timestamp
from duwi_smarthome_sdk.const.const import URL
from duwi_smarthome_sdk.util.http import post
from duwi_smarthome_sdk.model.req.device_control import ControlDevice

_LOGGER = logging.getLogger(__name__)


class ControlClient:

    def __init__(self,
                 app_key: str,
                 app_secret: str,
                 access_token: str,
                 app_version: str,
                 client_version: str,
                 address: str = None,
                 client_model: str = None,
                 is_group: bool = False
                 ):
        self._url = URL if address is None else address
        self._app_key = app_key
        self._app_secret = app_secret
        self._access_token = access_token
        self._app_version = app_version
        self._client_version = client_version
        self._client_model = client_model
        self._is_group = is_group

    async def control(self, body: Optional[ControlDevice]) -> str:
        body_string = json.dumps(body.to_dict(), separators=(',', ':')) if body else ""

        timestamp = current_timestamp()

        sign = md5_encrypt(f"{body_string}{self._app_secret}{timestamp}")

        headers = {
            'Content-Type': 'application/json',
            'accessToken': self._access_token,
            'appkey': self._app_key,
            'secret': self._app_secret,
            'time': str(timestamp),
            'sign': sign,
            'appVersion': self._app_version,
            'clientVersion': self._client_version,
            'clientModel': self._client_model,
        }
        global status
        body_dict = body.to_dict() if body else None
        if self._is_group:
            status, message, res = await post(f"{self._url}/deviceGroup/batchCommandOperate", headers, body_dict)
            _LOGGER.info("message %s res %s", message, res)
        else:
            status, message, res = await post(f"{self._url}/device/batchCommandOperate", headers, body_dict)
            _LOGGER.info("message %s res %s", message, res)

        return status



