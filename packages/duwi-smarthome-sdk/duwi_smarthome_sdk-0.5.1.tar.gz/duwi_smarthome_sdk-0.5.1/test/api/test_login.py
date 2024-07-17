from unittest import TestCase

from duwi_smarthome_sdk_dev.api.account import AccountClient
import asyncio


class TestLoginClient(TestCase):
    def test_login(self):
        async def run_test():
            cc = AccountClient(
                app_key="xxx",
                app_secret="xxx",
                app_version="0.0.1",
                client_version="0.0.1",
                client_model="homeassistant",
            )

            res = await cc.login(phone="phone", password="password")
            print(res)

        asyncio.run(run_test())
