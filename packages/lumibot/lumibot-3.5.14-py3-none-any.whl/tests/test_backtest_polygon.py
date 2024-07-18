import datetime
import os
from collections import defaultdict

import pandas_market_calendars as mcal
import pytz
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.entities import Asset
from lumibot.strategies import Strategy

# Global parameters
# API Key for testing Polygon.io
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")


class PolygonBacktestStrat(Strategy):
    parameters = {"symbol": "AMZN"}

    # Set the initial values for the strategy
    def initialize(self, parameters=None):
        self.sleeptime = "1D"
        self.first_price = None
        self.first_option_price = None
        self.orders = []
        self.prices = {}
        self.chains = {}
        self.market_opens_called = False
        self.market_closes_called = False
        # Track times to test LifeCycle order methods. Format: {order_id: {'fill': timestamp, 'submit': timestamp}}
        self.order_time_tracker = defaultdict(lambda: defaultdict(datetime.datetime))

    def select_option_expiration(self, chain, days_to_expiration=1):
        """
        Select the option expiration date based on the number of days (from today) until expiration
        :param chain: List of valid option contracts and their expiration dates and strike prices.
            Format: {'TradingClass': 'SPY', 'Multiplier': 100, 'Expirations': [], 'Strikes': []}
        :param days_to_expiration: Number of days until expiration, will select the next expiration date at or after
            this that is available on the exchange
        :return: option expiration as a datetime.date object
        """
        market_cal = mcal.get_calendar("NYSE")  # Typically NYSE, but can be different for some assets
        today = self.get_datetime()
        extra_days_padding = 7  # Some options are not traded every day. Make sure we get enough trading days to check

        # Trading Days DataFrame Format:
        #       index               market_open              market_close
        # =========== ========================= =========================
        #  2012-07-02 2012-07-02 13:30:00+00:00 2012-07-02 20:00:00+00:00
        #  2012-07-03 2012-07-03 13:30:00+00:00 2012-07-03 17:00:00+00:00
        #  2012-07-05 2012-07-05 13:30:00+00:00 2012-07-05 20:00:00+00:00
        trading_days_df = market_cal.schedule(
            start_date=today,
            end_date=today + datetime.timedelta(days=days_to_expiration + extra_days_padding)
        )

        # Look for the next trading day that is in the list of expiration dates. Skip the first trading day because
        # that is today and we want to find the next expiration date.
        #   Date Format: 2023-07-31
        trading_datestrs = [x.to_pydatetime().date() for x in trading_days_df.index.to_list()]
        for trading_day in trading_datestrs[days_to_expiration:]:
            day_str = trading_day.strftime("%Y-%m-%d")
            if day_str in chain['Expirations']:
                return trading_day

        raise ValueError(f"Could not find an option expiration date for {days_to_expiration} day(s) "
                         f"from today({today})")

    def before_market_opens(self):
        underlying_asset = Asset(self.parameters["symbol"])
        self.market_opens_called = True
        self.chains = self.get_chains(underlying_asset)

    def after_market_closes(self):
        orders = self.get_orders()
        self.market_closes_called = True
        self.log_message(f"PolygonBacktestStrat: {len(orders)} orders executed today")

    def on_filled_order(self, position, order, price, quantity, multiplier):
        self.log_message(f"PolygonBacktestStrat: Filled Order: {order}")
        self.order_time_tracker[order.identifier]['fill'] = self.get_datetime()

    def on_new_order(self, order):
        self.log_message(f"PolygonBacktestStrat: New Order: {order}")
        self.order_time_tracker[order.identifier]['submit'] = self.get_datetime()

    def on_canceled_order(self, order):
        self.log_message(f"PolygonBacktestStrat: Canceled Order: {order}")
        self.order_time_tracker[order.identifier]['cancel'] = self.get_datetime()

    # Trading Strategy: Backtest will only buy traded assets on first iteration
    def on_trading_iteration(self):
        if self.first_iteration:
            now = self.get_datetime()

            # Create simple option chain | Plugging Amazon "AMZN"; always checking Friday (08/04/23) ensuring
            # Traded_asset exists
            underlying_asset = Asset(self.parameters["symbol"])
            current_asset_price = self.get_last_price(underlying_asset)

            # Option Chain: Get Full Option Chain Information
            chain = self.get_chain(self.chains, exchange="SMART")
            expiration = self.select_option_expiration(chain, days_to_expiration=1)
            # expiration = datetime.date(2023, 8, 4)

            strike_price = round(current_asset_price)
            option_asset = Asset(
                symbol=underlying_asset.symbol,
                asset_type="option",
                expiration=expiration,
                right="CALL",
                strike=strike_price,
                multiplier=100,
                currency="USD",
            )
            current_option_price = self.get_last_price(option_asset)

            # Buy 10 shares of the underlying asset for the test
            qty = 10
            self.log_message(f"Buying {qty} shares of {underlying_asset} at {current_asset_price} @ {now}")
            order_underlying_asset = self.create_order(underlying_asset, quantity=qty, side="buy")
            submitted_order = self.submit_order(order_underlying_asset)
            self.orders.append(submitted_order)
            self.prices[submitted_order.identifier] = current_asset_price

            # Buy 1 option contract for the test
            order_option_asset = self.create_order(option_asset, quantity=1, side="buy")
            submitted_order = self.submit_order(order_option_asset)
            self.orders.append(submitted_order)
            self.prices[submitted_order.identifier] = current_option_price

            # Set a stop loss on the underlying asset and cancel it later to test the on_canceled_order() method
            stop_loss_order = self.create_order(underlying_asset, quantity=qty, side="sell",
                                                stop_price=current_asset_price - 20)
            submitted_order = self.submit_order(stop_loss_order)
            self.orders.append(submitted_order)

        # Not the 1st iteration, cancel orders.
        else:
            self.cancel_open_orders()


class TestPolygonBacktestFull:
    def test_polygon_restclient(self):
        """
        Test Polygon REST Client with Lumibot Backtesting and real API calls to Polygon. Using the Amazon stock
        which only has options expiring on Fridays. This test will buy 10 shares of Amazon and 1 option contract
        in the historical 2023-08-04 period (in the past!).
        """
        
        # Parameters: True = Live Trading | False = Backtest
        # trade_live = False
        backtesting_start = datetime.datetime(2023, 8, 1)
        backtesting_end = datetime.datetime(2023, 8, 4)

        # Execute Backtest | Polygon.io API Connection
        results, poly_strat_obj = PolygonBacktestStrat.run_backtest(
            PolygonDataBacktesting,
            backtesting_start,
            backtesting_end,
            benchmark_asset="SPY",
            show_plot=False,
            show_tearsheet=False,
            save_tearsheet=False,
            polygon_api_key=POLYGON_API_KEY,  # TODO Replace with Lumibot owned API Key
            # Painfully slow with free subscription setting b/c lumibot is over querying and imposing a very
            # strict rate limit
            polygon_has_paid_subscription=True,
        )
        assert results
        assert isinstance(poly_strat_obj, PolygonBacktestStrat)

        # Checks bug where LifeCycle methods not being called during PANDAS backtesting
        assert poly_strat_obj.market_opens_called
        assert poly_strat_obj.market_closes_called

        assert len(poly_strat_obj.orders) == 3  # Stock, option, stoploss all submitted
        assert len(poly_strat_obj.prices) == 2
        stock_order = poly_strat_obj.orders[0]
        option_order = poly_strat_obj.orders[1]
        stoploss_order = poly_strat_obj.orders[2]
        asset_order_id = stock_order.identifier
        option_order_id = option_order.identifier
        stoploss_order_id = stoploss_order.identifier
        assert asset_order_id in poly_strat_obj.prices
        assert option_order_id in poly_strat_obj.prices
        assert 130.0 < poly_strat_obj.prices[asset_order_id] < 140.0, "Valid asset price between 130 and 140"
        assert 130.0 < stock_order.get_fill_price() < 140.0, "Valid asset price between 130 and 140"
        assert poly_strat_obj.prices[option_order_id] == 4.10, "Opening Price is $4.10 on 08/01/2023"
        assert option_order.get_fill_price() == 4.10, "Fills at 1st candle open price of $4.10 on 08/01/2023"

        assert option_order.is_filled()

        # Check that the on_*_order methods were called
        # Lumibot is autosubmitting 'sell_position' order on cancel to make it 4 total orders
        assert len(poly_strat_obj.order_time_tracker) >= 3
        # Stock order should have been submitted and filled
        assert asset_order_id in poly_strat_obj.order_time_tracker
        assert poly_strat_obj.order_time_tracker[asset_order_id]['submit']
        assert (poly_strat_obj.order_time_tracker[asset_order_id]['fill'] >=
                poly_strat_obj.order_time_tracker[asset_order_id]['submit'])
        # Option order should have been submitted and filled
        assert option_order_id in poly_strat_obj.order_time_tracker
        assert poly_strat_obj.order_time_tracker[option_order_id]['submit']
        assert (poly_strat_obj.order_time_tracker[option_order_id]['fill'] >=
                poly_strat_obj.order_time_tracker[option_order_id]['submit'])
        # Stoploss order should have been submitted and canceled
        assert stoploss_order_id in poly_strat_obj.order_time_tracker
        assert poly_strat_obj.order_time_tracker[stoploss_order_id]['submit']
        assert (poly_strat_obj.order_time_tracker[stoploss_order_id]['cancel'] >
                poly_strat_obj.order_time_tracker[stoploss_order_id]['submit'])
        assert 'fill' not in poly_strat_obj.order_time_tracker[stoploss_order_id]

    def test_polygon_legacy_backtest(self):
        """Test that the legacy backtest() function call works without returning the startegy object"""
        # Parameters: True = Live Trading | False = Backtest
        # trade_live = False
        backtesting_start = datetime.datetime(2023, 8, 1)
        backtesting_end = datetime.datetime(2023, 8, 4)

        # Execute Backtest | Polygon.io API Connection
        results = PolygonBacktestStrat.backtest(
            PolygonDataBacktesting,
            backtesting_start,
            backtesting_end,
            benchmark_asset="SPY",
            show_plot=False,
            show_tearsheet=False,
            save_tearsheet=False,
            polygon_api_key=POLYGON_API_KEY,  # TODO Replace with Lumibot owned API Key
            # Painfully slow with free subscription setting b/c lumibot is over querying and imposing a very
            # strict rate limit
            polygon_has_paid_subscription=True,
        )
        assert results
