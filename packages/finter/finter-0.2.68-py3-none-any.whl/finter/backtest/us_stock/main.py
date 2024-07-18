import numpy as np
from numba import njit
import pandas as pd
from finter.data import ContentFactory
from finter.data import ModelData
import datetime

from finter.backtest.simulator import Simulator
from finter.backtest.base import BacktestResult
from finter.backtest.core import (
    calculate_buy_sell_volumes,
    update_nav,
    update_valuation_and_cash,
    update_target_volume,
    execute_transactions,
)

# Todo
# - volcap
# - buy & hold frequency


class USStockBacktestor(Simulator):
    def __init__(
        self,
        position: pd.DataFrame,
        price: pd.DataFrame,
        initial_cash: np.float64,
        buy_fee_tax: np.float64,
        sell_fee_tax: np.float64,
        slippage: np.float64,
        hedged: bool = True,
    ) -> None:
        self.initial_cash = initial_cash
        self.hedged = hedged

        self.weight, self.price, self.dates, self.common_columns = self.preprocess_data(
            position, price.ffill()
        )

        self.initial_cash, self.dollar_price = us_currency_setting(
            position, self.initial_cash, self.hedged, self.dates
        )

        # Todo: matrix fee
        self.buy_fee_tax = buy_fee_tax / 10000
        self.sell_fee_tax = sell_fee_tax / 10000

        # Todo: matrix slipage
        self.slippage = slippage / 10000

        # Todo: user set buy price, sell price
        self.buy_price = self.price * (1 + self.slippage)
        self.sell_price = self.price * (1 - self.slippage)

        self.num_assets = self.weight.shape[1]
        self.num_days = self.weight.shape[0]

        self.initialize_variables()

        self._results = USBacktestResult(self)


class USBacktestResult(BacktestResult):
    def calculate_krw_value(self, data):
        return data * self.simulator.dollar_price.values.reshape(-1, 1)

    @property
    def nav(self) -> pd.DataFrame:
        return pd.DataFrame(
            self.calculate_krw_value(self.simulator.nav),
            index=self.simulator.dates,
            columns=["nav"],
        )

    @property
    def cash(self) -> pd.DataFrame:
        return pd.DataFrame(
            self.calculate_krw_value(self.simulator.cash),
            index=self.simulator.dates,
            columns=["cash"],
        )

    @property
    def valuation(self) -> pd.DataFrame:
        return pd.DataFrame(
            self.calculate_krw_value(
                self.simulator.valuation.sum(axis=1).reshape(-1, 1)
            ),
            index=self.simulator.dates,
            columns=["valuation"],
        )

    @property
    def cost(self) -> pd.DataFrame:
        cost = np.nansum(
            (
                self.simulator.actual_buy_volume
                * self.simulator.buy_price
                * self.simulator.buy_fee_tax
            )
            + (
                self.simulator.actual_sell_volume
                * self.simulator.sell_price
                * self.simulator.sell_fee_tax
            ),
            axis=1,
        ).reshape(-1, 1)
        return pd.DataFrame(
            self.calculate_krw_value(cost),
            index=self.simulator.dates,
            columns=["cost"],
        )

    @property
    def summary(self) -> pd.DataFrame:
        pnl = self.nav.diff().fillna(0) - self.cost.values
        pnl.columns = ("pnl",)

        result = pd.concat(
            [self.nav, self.cash, self.valuation, self.cost, pnl], axis=1
        )
        return result

    @property
    def realized_pnl(self) -> pd.DataFrame:
        return self.calculate_krw_value(
            (np.nan_to_num(self.simulator.sell_price) - self.average_buy_price.shift())
            * self.simulator.actual_sell_volume
        )

    @property
    def unrealized_pnl(self) -> pd.DataFrame:
        return self.calculate_krw_value(
            (np.nan_to_num(self.simulator.price) - self.average_buy_price)
            * self.simulator.actual_holding_volume
        )


def us_currency_setting(position, initial_cash, hedge, dates):
    # Load the exchange rate data
    dollar_price = ModelData.load("content.factset.api.currency.exchange_rate.1d")[
        "USDKRW"
    ]
    # Find the first non-zero position
    first_index = position.sum(axis=1).ne(0).idxmin()
    first_currency = dollar_price.loc[first_index]
    initial_cash /= first_currency

    # Reindex dollar_price to match position's index
    dollar_price = dollar_price.reindex(dates).ffill()

    if hedge:
        # Set all values to the first_currency if hedge is True
        dollar_price.iloc[:] = first_currency

    return initial_cash, dollar_price
