import logging
from datetime import datetime, timedelta

import pandas as pd

from lumibot.data_sources import DataSource
from lumibot.tools import print_progress_bar, to_datetime_aware


class DataSourceBacktesting(DataSource):
    IS_BACKTESTING_DATA_SOURCE = True

    def __init__(
        self, datetime_start, datetime_end, backtesting_started=None
    ):
        if backtesting_started is None:
            _backtesting_started = datetime.now()
        else:
            _backtesting_started = backtesting_started

        self.datetime_start = datetime_start
        self.datetime_end = datetime_end
        self._datetime = datetime_start
        self._iter_count = None
        self.backtesting_started = _backtesting_started

        # Subtract one minute from the datetime_end so that the strategy stops right before the datetime_end
        self.datetime_end -= timedelta(minutes=1)

    def get_datetime(self):
        return self._datetime

    def get_datetime_range(self, length, timestep="minute", timeshift=None):
        backtesting_timeshift = datetime.now() - self._datetime
        if timeshift:
            backtesting_timeshift += timeshift

        if timestep == "minute":
            period_length = length * timedelta(minutes=1)
            end_date = self.get_last_minute() - backtesting_timeshift
        else:
            period_length = length * timedelta(days=1)
            end_date = self.get_last_day() - backtesting_timeshift

        start_date = end_date - period_length
        return (start_date, end_date)

    def _update_datetime(self, new_datetime, cash=None, portfolio_value=None):
        self._datetime = new_datetime
        print_progress_bar(
            new_datetime,
            self.datetime_start,
            self.datetime_end,
            self.backtesting_started,
            cash=cash,
            portfolio_value=portfolio_value,
        )

    def _pull_source_symbol_bars(
        self,
        asset,
        length,
        timestep=None,
        timeshift=None,
        quote=None,
        exchange=None,
        include_after_hours=True,
    ):
        if exchange is not None:
            logging.warning(
                f"the exchange parameter is not implemented for DataSourceBacktesting, but {exchange} was passed as the exchange"
            )

        if timestep is None:
            timestep = self.get_timestep()
        if self.LIVE_DATA_SOURCE.SOURCE == "YAHOO":
            backtesting_timeshift = timeshift
        elif self.LIVE_DATA_SOURCE.SOURCE == "PANDAS":
            backtesting_timeshift = timeshift
        elif self.LIVE_DATA_SOURCE.SOURCE == "ALPHA_VANTAGE":
            backtesting_timeshift = timeshift
        else:
            raise ValueError(
                f"An incorrect data source type was received. Received"
                f" {self.LIVE_DATA_SOURCE.SOURCE}"
            )
        result = self.LIVE_DATA_SOURCE._pull_source_symbol_bars(
            self,
            asset,
            length,
            timestep=timestep,
            timeshift=backtesting_timeshift,
            quote=quote,
        )

        if result is None:
            return result
        else:
            return result
