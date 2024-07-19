import asyncio
from collections.abc import Callable
import pandas as pd
from flowtask.components.Azure import Azure
from flowtask.exceptions import ComponentError
from flowtask.conf import (
    AZURE_ADFS_TENANT_ID
)

class MS365Usage(Azure):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        self.report_type = kwargs.pop("report_type", "M365")
        self.usage_method = kwargs.pop("usage_method", "UserDetail")
        if self.report_type == 'M365':
            self._report = 'getM365App'
        elif self.report_type == 'Teams':
            self._report = 'getTeamsUserActivity'
            if self.usage_method == 'DeviceUserDetails':
                self._report = 'getTeamsDeviceUsage'
                self.usage_method = 'UserDetail'
            elif self.usage_method == 'DeviceUserCounts':
                self._report = 'getTeamsDeviceUsage'
            elif self.usage_method == 'DeviceDistributionUserCounts':
                self._report = 'getTeamsDeviceUsage'
                self.usage_method = 'DistributionUserCounts'
        elif self.report_type == 'SharePoint':
            self._report = 'getSharePointActivity'
        elif self.report_type == 'OneDrive':
            self._report = 'getOneDriveActivity'
        elif self.report_type == 'Yammer':
            self._report = 'getYammerActivity'
            if self.usage_method == 'DeviceUserDetails':
                self._report = 'getYammerDeviceUsage'
                self.usage_method = 'UserDetail'
            elif self.usage_method == 'DeviceUserCounts':
                self._report = 'getYammerDeviceUsage'
            elif self.usage_method == 'DeviceDistributionUserCounts':
                self._report = 'getYammerDeviceUsage'
                self.usage_method = 'DistributionUserCounts'
        else:
            self._report = 'getM365App'
        self.period = kwargs.pop("period", "D7")
        self.format = kwargs.pop("format", "text/csv")
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        super().start()

        self.method = "GET"
        self.download = False

        _base_url = "https://graph.microsoft.com/v1.0/reports/{report}{usage_method}(period='{period}')?$format={format}"
        self.url = _base_url.format(
            report=self._report,
            usage_method=self.usage_method,
            period=self.period,
            format=self.format
        )
        return True

    async def run(self):
        """Run Azure Connection for getting Users Info."""
        self._logger.info(f"<{__name__}>:")
        self.set_apikey()

        try:
            result, error = await self.async_request(self.url, self.method)

        except Exception as ex:
            raise ComponentError(f"Error getting {self.usage_method} from API") from ex
        df = await self.from_csv(result, header=0)
        self._result = df
        return self._result

    async def close(self):
        pass

    def set_apikey(self):
        self.app = self.get_msal_app()
        token, self.token_type = self.get_token()
        self.auth["apikey"] = token
