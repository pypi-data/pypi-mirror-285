import asyncio
from collections.abc import Callable
import pandas as pd
from ..exceptions import ComponentError, ConfigError
from .abstract import DtComponent


class tUnnest(DtComponent):
    """
    tUnnest.

    Split a Column into several rows, alternative with dropping source column.
    """
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        """Init Method."""
        self.source_column: str = kwargs.pop('source_column', None)
        self.destination: str = kwargs.get('destination', None)
        self.drop_source: bool = kwargs.get('drop_source', False)
        self.separator: str = kwargs.get('separator', ', ')
        if not self.source_column:
            raise ConfigError(
                "Missing Source_column for making unnest."
            )
        super(tUnnest, self).__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        if self.previous:
            self.data = self.input
        else:
            raise ComponentError(
                "Data Not Found",
                code=404
            )
        if not isinstance(self.data, pd.DataFrame):
            raise ComponentError("Incompatible Pandas Dataframe", code=404)
        if not self.destination:
            raise ConfigError(
                "Missing *destination* column for Unnest Rows."
            )
        return True

    async def close(self):
        pass

    async def run(self):
        try:
            # Split the column into multiple rows
            df = self.data.assign(
                **{
                    self.destination: self.data[self.source_column].str.split(self.separator)
                }
            ).explode(self.destination)
            if self.drop_source is True:
                # Drop the original column
                df = df.drop(columns=[self.source_column])
            self._result = df
            self.add_metric("NUM_ROWS", self._result.shape[0])
            self.add_metric("NUM_COLUMNS", self._result.shape[1])
            if self._debug:
                print("Debugging: tUnnest ===")
                print(self._result)
                columns = list(self._result.columns)
                for column in columns:
                    t = self._result[column].dtype
                    print(column, "->", t, "->", self._result[column].iloc[0])
            return self._result
        except Exception as err:
            raise ComponentError(
                f"Unknown error {err!s}"
            ) from err
