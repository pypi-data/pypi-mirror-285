from unittest import TestCase
from duwi_smarthome_sdk_dev.api.house import HouseInfoClient
import asyncio


class TestHouseInfoClient(TestCase):
    def test_discover(self):
        async def run_test():
            cc = HouseInfoClient(
                app_key="2e479831-1fb7-751e-7017-7534f7f99fc1",
                app_secret="26af4883a943083a4c34083897fcea10",
                access_token="715d1c63-85c0-4d74-9a89-5a0aa4806f74",
                app_version="0.0.1",
                client_version="0.0.1",
                client_model="homeassistant",
            )

            res = await cc.fetch_house_info()
            print(res)

        asyncio.run(run_test())
