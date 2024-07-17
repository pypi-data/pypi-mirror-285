import asyncio
from unittest import TestCase
from duwi_smarthome_sdk_dev.api.discover import DiscoverClient
from duwi_smarthome_sdk_dev.model.resp.device import Device


class TestDiscoverClient(TestCase):
    def test_discover(self):
        async def run_test():
            cc = DiscoverClient(
                app_key="2e479831-1fb7-751e-7017-7534f7f99fc1",
                app_secret="26af4883a943083a4c34083897fcea10",
                access_token="715d1c63-85c0-4d74-9a89-5a0aa4806f74",
                app_version="0.0.1",
                client_version="0.0.1",
                client_model="homeassistant",
            )

            status,devices = await cc.discover(
                house_no="c7bf567d-225a-4533-ab72-5dc080b794f5",
            )
            print(status)
            for d in devices:
                if d.device_type_no.startswith("8"):
                    print(d)
            print(1)
        asyncio.run(run_test())
