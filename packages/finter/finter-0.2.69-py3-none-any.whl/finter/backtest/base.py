import numpy as np
import pandas as pd

# Todo
# - volcap
# - buy & hold frequency


class BaseBacktestor:
    def __init__(
        self,
        position: pd.DataFrame,
        price: pd.DataFrame,
        initial_cash: np.float64,
        buy_fee_tax: np.float64,
        sell_fee_tax: np.float64,
        slippage: np.float64,
    ) -> None:
        self.weight, self.price, self.dates, self.common_columns = self.preprocess_data(
            position, price
        )
        self.initial_cash = initial_cash

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

        self._results = BacktestResult(self)

    def preprocess_data(self, position: pd.DataFrame, price: pd.DataFrame) -> tuple:
        weight = position / 1e8
        common_columns = weight.columns.intersection(price.columns)

        weight = weight[common_columns]
        price = price[common_columns]

        first_position_index = weight.index[0]
        price_index_pos = price.index.get_loc(first_position_index)

        if price_index_pos == 0:
            price_index_pos = 1

        price = price.iloc[price_index_pos - 1 : price_index_pos + len(weight)]
        weight = weight.reindex(price.index)

        return weight.to_numpy(), price.to_numpy(), weight.index, common_columns

    def initialize_variables(self) -> None:
        shape = (self.num_days, self.num_assets)

        self.actual_holding_volume = np.full(shape, np.nan, dtype=np.float64)
        self.target_volume = np.full(shape, np.nan, dtype=np.float64)
        self.target_buy_volume = np.full(shape, np.nan, dtype=np.float64)
        self.target_sell_volume = np.full(shape, np.nan, dtype=np.float64)
        self.actual_sell_volume = np.full(shape, np.nan, dtype=np.float64)
        self.actual_sell_amount = np.full(shape, np.nan, dtype=np.float64)
        self.available_buy_amount = np.full(
            (self.num_days, 1), np.nan, dtype=np.float64
        )
        self.target_buy_amount = np.full(shape, np.nan, dtype=np.float64)
        self.target_buy_amount_sum = np.full(
            (self.num_days, 1), np.nan, dtype=np.float64
        )
        self.available_buy_volume = np.full(shape, np.nan, dtype=np.float64)
        self.actual_buy_volume = np.full(shape, np.nan, dtype=np.float64)
        self.actual_buy_amount = np.full(shape, np.nan, dtype=np.float64)
        self.valuation = np.full(shape, np.nan, dtype=np.float64)
        self.cash = np.full((self.num_days, 1), np.nan, dtype=np.float64)
        self.nav = np.full((self.num_days, 1), np.nan, dtype=np.float64)

        self.actual_holding_volume[0] = 0
        self.cash[0] = self.initial_cash
        self.nav[0] = self.initial_cash

    def run(self):
        raise NotImplementedError(
            "The backtest method should be implemented by subclasses"
        )

    @property
    def result(self):
        return self._results

    @property
    def summary(self):
        return self._results.summary


class BacktestResult:
    def __init__(self, simulator: BaseBacktestor) -> None:
        self.simulator = simulator

    @property
    def nav(self) -> pd.DataFrame:
        return pd.DataFrame(
            self.simulator.nav, index=self.simulator.dates, columns=["nav"]
        )

    @property
    def cash(self) -> pd.DataFrame:
        return pd.DataFrame(
            self.simulator.cash, index=self.simulator.dates, columns=["cash"]
        )

    @property
    def valuation(self) -> pd.DataFrame:
        return pd.DataFrame(
            self.simulator.valuation.sum(axis=1),
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
        )
        return pd.DataFrame(
            cost,
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
    def average_buy_price(self) -> pd.DataFrame:
        shape = (self.simulator.num_days, self.simulator.num_assets)

        self.cummulative_buy_amount = np.full(shape, np.nan, dtype=np.float64)
        self.__average_buy_price = np.full(shape, np.nan, dtype=np.float64)

        self.cummulative_buy_amount[0] = 0
        self.__average_buy_price[0] = 0

        for i in range(1, self.simulator.num_days):
            self.cummulative_buy_amount[i] = (
                self.cummulative_buy_amount[i - 1]
                + (
                    self.simulator.actual_buy_volume[i]
                    * np.nan_to_num(self.simulator.buy_price[i])
                )
                - (
                    self.simulator.actual_sell_volume[i]
                    * self.__average_buy_price[i - 1]
                )
            )

            self.__average_buy_price[i] = np.nan_to_num(
                self.cummulative_buy_amount[i] / self.simulator.actual_holding_volume[i]
            )

        return pd.DataFrame(
            self.__average_buy_price,
            index=self.simulator.dates,
            columns=self.simulator.common_columns,
        )

    @property
    def realized_pnl(self) -> pd.DataFrame:
        return (
            np.nan_to_num(self.simulator.sell_price) - self.average_buy_price.shift()
        ) * self.simulator.actual_sell_volume

    @property
    def unrealized_pnl(self) -> pd.DataFrame:
        return (
            np.nan_to_num(self.simulator.price) - self.average_buy_price
        ) * self.simulator.actual_holding_volume
