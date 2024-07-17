import asyncio
from unittest import TestCase
from duwi_smarthome_sdk.api.control import ControlClient
from duwi_smarthome_sdk.model.req.device_control import ControlDevice


class TestControlClient(TestCase):
    def test_control(self):
        async def run_test():
            for i in range(100):
                cc = ControlClient(
                    app_key='2e479831-1fb7-751e-7017-7534f7f99fc1',
                    app_secret='26af4883a943083a4c34083897fcea10',
                    access_token='715d1c63-85c0-4d74-9a89-5a0aa4806f74',
                    app_version="0.0.1",
                    client_version="0.0.1",
                    client_model="homeassistant",
                    address="http://8.140.128.174:8019/homeApi/v1"
                )
                cd = ControlDevice(
                    device_no="0101A0000017-1",
                    house_no="a80031c5-2f69-42bb-ab44-e3f46944bc2f",
                )
                cd.add_param_info("switch", "on")
                res = await cc.control(cd)
                print(i, res)

        asyncio.run(run_test())
