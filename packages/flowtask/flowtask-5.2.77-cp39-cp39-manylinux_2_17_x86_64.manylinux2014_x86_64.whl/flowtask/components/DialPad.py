import asyncio
from collections.abc import Callable
from urllib.parse import urljoin
from flowtask.components.abstract import DtComponent
from flowtask.components.interfaces.http import HTTPService
from flowtask.exceptions import ComponentError


class DialPad(DtComponent, HTTPService):

    accept: str = "application/json"
    download = None
    _credentials: dict = {"APIKEY": str}

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        DtComponent.__init__(self, loop=loop, job=job, stat=stat, **kwargs)
        HTTPService.__init__(self, **kwargs)

    async def start(self, **kwargs):
        self._base_url = "https://dialpad.com/api/v2/"

        self.processing_credentials()
        self.auth = {"apikey": self.credentials["APIKEY"]}

        return True

    async def dialpad_stats(self):
        # processing statistics asynchronously
        stats_url = urljoin(self._base_url, "stats/")
        processing_result, _ = await self.session(
            stats_url, "post", data=self.body_params, use_json=True
        )
        request_id = processing_result.get("request_id")

        get_result_url = urljoin(stats_url, request_id)
        response_result, _ = await self.session(get_result_url, use_json=True)
        file_url = response_result.get("download_url")

        self.download = False
        result, _ = await self.session(file_url)

        return result

    async def run(self):
        try:
            method = getattr(self, f"dialpad_{self.type}")
        except AttributeError as ex:
            raise ComponentError(f"{__name__}: Wrong 'type' on task definition") from ex

        result = await method()

        df_results = await self.from_csv(result)

        self._result = df_results
        return self._result

    async def close(self):
        pass

    def processing_credentials(self):
        if self.credentials:
            for value, dtype in self._credentials.items():
                try:
                    if type(self.credentials[value]) == dtype:
                        default = getattr(self, value, self.credentials[value])
                        val = self.get_env_value(
                            self.credentials[value], default=default
                        )
                        self.credentials[value] = val
                except (TypeError, KeyError) as ex:
                    self._logger.error(f"{__name__}: Wrong or missing Credentials")
                    raise ComponentError(
                        f"{__name__}: Wrong or missing Credentials"
                    ) from ex
