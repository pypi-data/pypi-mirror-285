import pandas as pd
from finter.data import ContentFactory
from finter.settings import logger


class BuyHoldConverter:
    # 기본 : position rebalancing 주기마다.
    # parameter -> 1 week, mothly, quarterly rebalancing
    def basic_converter(self, df, universe):
        # 시작일과 종료일 계산
        start, end = df.index[0], df.index[-1]
        start = (
            (start.year * 10000 + 101)
            if start.month == 1
            else ((start.year - 1) * 10000 + 1201)
        )
        end = end.year * 10000 + end.month * 100 + end.day

        # 합계가 0이 아닌 열만 남김
        df = df.loc[:, df.sum() != 0]

        # Universe에 따른 가격 데이터 가져오기
        cf = ContentFactory(universe, start, end)
        price_key = "price_close" if universe == "kr_stock" else "us-etf-price_close"
        self.prc = cf.get_df(price_key)[df.columns]

        # 원본 및 변환 데이터프레임 복사
        df_transformed = df.copy()
        prc_change = self.prc.pct_change(1, fill_method="pad").fillna(0)
        prc_change = prc_change.loc[df.index]

        # 첫 행은 그대로 유지하고, 이후의 행들에 대해 변환 적용
        for i in range(1, df.shape[0]):
            # 이전 행과 현재 행의 값이 동일한지 비교
            if (df.iloc[i] == df.iloc[i - 1]).all():
                # prc_change 적용하여 값 변환
                df_transformed.iloc[i] = df_transformed.iloc[i - 1] * (
                    1 + prc_change.iloc[i - 1]
                )
                # 합계를 원래 값과 같게 유지
                df_transformed.iloc[i] /= (
                    df_transformed.iloc[i].sum() / df.iloc[i].sum()
                )
            else:
                # 값이 다르면 원래 값을 유지
                df_transformed.iloc[i] = df.iloc[i]

        return df_transformed

    def fixed_converter(self, df, universe, rebalancing_period):
        # 시작일과 종료일 계산
        start, end = df.index[0], df.index[-1]
        start = (
            (start.year * 10000 + 101)
            if start.month == 1
            else ((start.year - 1) * 10000 + 1201)
        )
        end = end.year * 10000 + end.month * 100 + end.day

        # 합계가 0이 아닌 열만 남김
        df = df.loc[:, df.sum() != 0]

        # Universe에 따라 ContentFactory에서 가격 데이터 가져오기
        if universe == "kr_stock":
            cf = ContentFactory("kr_stock", start, end)
            self.prc = cf.get_df("price_close")[df.columns]
        elif universe == "us_etf":
            cf = ContentFactory("us_etf", start, end)
            self.prc = cf.get_df("us-etf-price_close")[df.columns]

        df_transformed = df.copy()
        prc_change = self.prc.pct_change(1, fill_method="pad").fillna(0)
        prc_change = prc_change.loc[df.index]

        if isinstance(rebalancing_period, int):
            rebalancing_dates = df.index[::rebalancing_period]
        else:
            if rebalancing_period == "weekly":
                freq = "W-MON"
            elif rebalancing_period == "monthly":
                freq = "MS"
            elif rebalancing_period == "quarterly":
                freq = "QS"
            else:
                raise ValueError(
                    "Invalid rebalancing_period. Use integer or one of ['weekly', 'monthly', 'quarterly']"
                )

            # 각 주기의 첫 거래 가능한 날짜 찾기
            potential_rebalancing_dates = df.resample(freq).first().index
            rebalancing_dates = []
            for date in potential_rebalancing_dates:
                valid_dates = df.index[df.index >= date]
                if len(valid_dates) > 0:
                    rebalancing_dates.append(valid_dates[0])
            rebalancing_dates = pd.DatetimeIndex(rebalancing_dates)

        # 리밸런싱 및 포지션 유지
        for i in range(1, df.shape[0]):
            if df.index[i] in rebalancing_dates:
                df_transformed.iloc[i] = df.iloc[i]
            else:
                df_transformed.iloc[i] = df_transformed.iloc[i - 1] * (
                    1 + prc_change.iloc[i - 1]
                )
                df_transformed.iloc[i] /= (
                    df_transformed.iloc[i].sum() / df.iloc[i].sum()
                )

        logger.info(
            f"The first rebalancing day is {rebalancing_dates[0]}. It should be earlier than the position start date of the get function."
        )

        return df_transformed
