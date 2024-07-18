import numpy as np
from numba import njit


@njit
def update_target_volume(
    weight: np.ndarray, prev_nav: np.float64, prev_price: np.ndarray
) -> np.ndarray:
    return np.nan_to_num(weight * prev_nav / prev_price)


@njit
def calculate_buy_sell_volumes(
    target_volume: np.ndarray,
    prev_actual_holding_volume: np.ndarray,
    available_sell_volume: np.ndarray = None,
) -> tuple:
    target_buy_volume = np.maximum(target_volume - prev_actual_holding_volume, 0)
    target_sell_volume = np.maximum(prev_actual_holding_volume - target_volume, 0)

    if available_sell_volume is not None:
        actual_sell_volume = np.minimum(available_sell_volume, target_sell_volume)
    else:
        actual_sell_volume = target_sell_volume

    return target_buy_volume, target_sell_volume, actual_sell_volume


@njit
def execute_transactions(
    actual_sell_volume: np.ndarray,
    buy_price: np.ndarray,
    buy_fee_tax: np.float64,
    sell_price: np.ndarray,
    sell_fee_tax: np.float64,
    prev_cash: np.float64,
    target_buy_volume: np.ndarray,
) -> tuple:
    actual_sell_amount = np.nan_to_num(
        actual_sell_volume * sell_price * (1 - sell_fee_tax)
    )
    available_buy_amount = prev_cash + actual_sell_amount.sum()
    target_buy_amount = np.nan_to_num(target_buy_volume * buy_price * (1 + buy_fee_tax))
    target_buy_amount_sum = target_buy_amount.sum()
    if target_buy_amount_sum > 0:
        available_buy_volume = np.nan_to_num(
            (target_buy_amount / target_buy_amount_sum)
            * (available_buy_amount / (buy_price * (1 + buy_fee_tax)))
        )
        actual_buy_volume = np.minimum(available_buy_volume, target_buy_volume)
        actual_buy_amount = np.nan_to_num(
            actual_buy_volume * buy_price * (1 + buy_fee_tax)
        )
    else:
        actual_buy_volume = np.zeros_like(target_buy_volume)
        actual_buy_amount = np.zeros_like(target_buy_volume)
    return (
        actual_sell_amount,
        available_buy_amount,
        actual_buy_volume,
        actual_buy_amount,
    )


@njit
def update_valuation_and_cash(
    prev_actual_holding_volume: np.ndarray,
    actual_buy_volume: np.ndarray,
    actual_sell_volume: np.ndarray,
    price: np.ndarray,
    available_buy_amount: np.float64,
    actual_buy_amount: np.ndarray,
) -> tuple:
    actual_holding_volume = (
        prev_actual_holding_volume + actual_buy_volume - actual_sell_volume
    )
    valuation = np.nan_to_num(actual_holding_volume * price)
    cash = available_buy_amount - actual_buy_amount.sum()
    return actual_holding_volume, valuation, cash


@njit
def update_nav(cash: np.float64, valuation: np.ndarray) -> np.float64:
    return cash + valuation.sum()
