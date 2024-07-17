import asyncio

from duwi_smarthome_sdk_dev.api.terminal import TerminalClient


class TestTerminalClient:
    def test_discover(self):
        async def run_test():
            cc = TerminalClient(
                app_key="2e479831-1fb7-751e-7017-7534f7f99fc1",
                app_secret="26af4883a943083a4c34083897fcea10",
                access_token="715d1c63-85c0-4d74-9a89-5a0aa4806f74",
                app_version="0.0.1",
                client_version="0.0.1",
                client_model="homeassistant",
            )

            for i in range(30):
                res = await cc.fetch_terminal_info(
                    house_no="c7bf567d-225a-4533-ab72-5dc080b794f5"
                )

                print(res)

        asyncio.run(run_test())
