from finter.framework_model.content import Loader
from finter.framework_model.content_loader.krx.fnguide.helper import (
    fnguide_entity_id_to_dataguide_ccid,
)
import pandas as pd


class KrFinancialLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    @staticmethod
    def _filter_dup_val(s, pair, k_lst=[]):
        if isinstance(s, pd.Series):
            key_list = []
            return s.apply(
                lambda x: KrFinancialLoader._filter_dup_val(x, pair, key_list)
            )
        elif isinstance(s, dict):
            val = {}
            for k, v in s.items():
                if pair and ([k, v] not in k_lst):
                    k_lst.append([k, v])
                    val[k] = s[k]
                elif not pair and (k not in k_lst):
                    k_lst.append(k)
                    val[k] = s[k]
            return val

    def get_df(
        self,
        start: int,
        end: int,
        fill_nan=True,
        preprocess_type: str = None,
        dataguide_ccid=False,
        *args,
        **kwargs,
    ):
        raw = self._load_cache(
            self.__CM_NAME,
            start,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
            *args,
            **kwargs,
        )
        if preprocess_type == "unpivot":
            unpivot_df = (
                (
                    raw
                    if kwargs.get("code_format") == "cmp_cd"
                    else fnguide_entity_id_to_dataguide_ccid(raw)
                )
                .unstack()
                .dropna()
                .reset_index()
            )
            unpivot_df.columns = [
                "short_code" if kwargs.get("code_format") == "cmp_cd" else "ccid",
                "pit",
                "val",
            ]
            m = (
                pd.DataFrame([*unpivot_df["val"]], unpivot_df.index)
                .stack()
                .rename_axis([None, "fiscal"])
                .reset_index(1, name="value")
            )
            result = unpivot_df[
                [
                    "short_code" if kwargs.get("code_format") == "cmp_cd" else "ccid",
                    "pit",
                ]
            ].join(m)
            return result
        elif preprocess_type == "duplicated_pair":
            raw = raw.apply(lambda x: KrFinancialLoader._filter_dup_val(x, pair=True))
            raw = raw.where(raw.astype(bool))
        elif preprocess_type == "duplicated_fiscal":
            raw = raw.apply(lambda x: KrFinancialLoader._filter_dup_val(x, pair=False))
            raw = raw.where(raw.astype(bool))
        else:
            pass

        # todo: check if remove id convert logic in parquet
        return raw.dropna(how="all")
        # return (
        #     raw
        #     if kwargs.get("code_format")
        #     else fnguide_entity_id_to_dataguide_ccid(raw)
        # ).dropna(how="all")
