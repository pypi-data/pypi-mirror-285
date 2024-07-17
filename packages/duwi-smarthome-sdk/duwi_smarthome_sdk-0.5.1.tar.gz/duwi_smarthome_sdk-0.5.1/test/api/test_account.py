from unittest import TestCase

from duwi_smarthome_sdk.api.account import AccountClient
import asyncio


class TestLoginClient(TestCase):
    def test_auth(self):
        async def run_test():
            cc = AccountClient(
                address="http://8.140.128.174:8019/homeApi/v1",
                app_key="2e479831-1fb7-751e-7017-7534f7f99fc1",
                app_secret="26af4883a943083a4c34083897fcea10",
                app_version="0.0.1",
                client_version="0.0.1",
                client_model="homeassistant",
            )

            res = await cc.auth(app_key="2e479831-1fb7-751e-7017-7534f7f99fc1",
                                app_secret="26af4883a943083a4c34083897fcea10")
            print(res)

        asyncio.run(run_test())
