import asyncio
import pandas as pd
from flowtask.components.abstract import DtComponent
from flowtask.exceptions import ComponentError
from xmlrpc.client import ServerProxy


class Odoo(DtComponent):
    _credentials: dict = {
        "HOST": str,
        "PORT": str,
        "DB": str,
        "USERNAME": str,
        "PASSWORD": str,
    }

    async def start(self, **kwargs):
        if self.previous:
            self.data = self.input

        self.processing_credentials()

        self.common = self.get_server_proxy("common")
        self.uid = self.common.authenticate(
            self.credentials["DB"],
            self.credentials["USERNAME"],
            self.credentials["PASSWORD"],
            {},
        )

        self.models = self.get_server_proxy("object")

        return True

    async def run(self):
        method_call = getattr(self, f"odoo_{self.method}")

        if not method_call:
            raise ComponentError("incorrect method or method not provided")
        
        method_call_task = asyncio.to_thread(method_call)

        method_call_result = await method_call_task

        df = pd.DataFrame(method_call_result)
        self._result = df

        return self._result

    async def close(self):
        return True

    def get_server_proxy(self, endpoint):
        return ServerProxy(
            "{}:{}/xmlrpc/2/{}".format(
                self.credentials["HOST"], self.credentials["PORT"], endpoint
            )
        )

    def model_call(self, method, *args, **kwargs):
        return self.models.execute_kw(
            self.credentials["DB"],
            self.uid,
            self.credentials["PASSWORD"],
            self.model,
            method,
            *args,
            **kwargs,
        )

    def get_values_from_previous_data(self, field=None):
        if isinstance(self.data, pd.DataFrame) and not self.data.empty:
            if not field:
                return [self.data.to_dict("records")]

            return [[(field, "in", self.data[field].to_list())]] or [[]]

    def odoo_search_read(self):
        prev_step_field = getattr(self, "use_field_from_previous_step", None)

        domain = getattr(
            self,
            "domain",
            self.get_values_from_previous_data(prev_step_field),
        )
        fields = getattr(self, "fields", {})

        return self.model_call(
            "search_read", domain or [], fields and {"fields": fields}
        )

    def odoo_create(self):
        try:
            # values on step arguments have precedence
            values = getattr(self, "values", self.get_values_from_previous_data())
            assert values

            return self.model_call("create", values)

        except AssertionError:
            raise ComponentError('"values" required for "create" method')

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
