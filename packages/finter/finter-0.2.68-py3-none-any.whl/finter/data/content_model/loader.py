import fnmatch

from finter import BaseAlpha
from finter.api.content_api import ContentApi
from finter.data.content_model.catalog_sheet import get_data
from finter.settings import get_api_client, logger


class ContentFactory:
    """
    A class representing a content model (CM) factory that generates and manages content models
    based on a specified universe name and a time range.

    Attributes:
        start (int): Start date for the content in YYYYMMDD format.
        end (int): End date for the content in YYYYMMDD format.
        universe_name (str): Name of the universe to base content models on.
        match_list (list[str]): Patterns used to match content models based on the universe name.
        cm_dict (dict[str, list[str]]): Dictionary mapping content match patterns to lists of corresponding content model names.

    Methods:
        get_df(item_name: str) -> pd.DataFrame:
            Retrieves the DataFrame associated with a specified item name.
        get_full_cm_name(item_name: str) -> str:
            Retrieves the full content model name for a specified item name.
        determine_base() -> list[str]:
            Determines the base match patterns for content models based on the universe name.
        get_cm_dict() -> dict:
            Generates the content model dictionary based on the universe's match list.
        show():
            Displays an interactive widget for exploring content model information in a scrollable list format.

    Property:
        item_list (list[str]): Provides a sorted list of unique item names from the content model dictionary.
    """

    def __init__(self, universe_name: str, start: int, end: int):
        """
        Initializes the ContentFactory with the specified universe name, start date, and end date.

        Args:
            universe_name (str): The name of the universe which the content models are based on.
                Example: 'raw', 'kr_stock'.
            start (int): The start date for the content in YYYYMMDD format.
                Example: 20210101.
            end (int): The end date for the content in YYYYMMDD format.
                Example: 20211231.

        Raises:
            ValueError: If the universe name is not supported.
        """
        self.client = get_api_client()
        self.start = start
        self.end = end
        self.universe_name = universe_name

        # Todo: Migrate universe with db or gs sheet or ...
        self.gs_df = get_data()

        self.match_list = self.determine_base()
        self.cm_dict = self.get_cm_dict()

    # Todo: check generate dependency when submit alpha
    def get_df(self, item_name, category=None, freq="1d", **kwargs):
        cm_name = self.get_full_cm_name(item_name, category, freq)
        param = {"start": self.start, "end": self.end}
        param.update(kwargs)
        if self.client.user_group in ["free_tier", "data_beta"]:
            param["code_format"] = "short_code"
            param["trim_short"] = True
            if "ftp.financial" in cm_name or "ftp.consensus" in cm_name:
                param["code_format"] = "cmp_cd"
        df = BaseAlpha.get_cm(cm_name).get_df(**param)
        return df

    # Todo: Dealing duplicated item name later
    def get_full_cm_name(self, item_name, category=None, freq="1d"):
        if self.universe_name == "raw":
            return item_name

        try:
            cm_list = [
                key.replace("*", item_name)
                for key, items in self.cm_dict.items()
                if item_name in items
            ]
            if len(cm_list) > 1:
                logger.info(
                    f"""
                    Multiple matching cm are detected
                    Matching cm list : {str([cm_name.split('.')[3] + '.' + item_name + '.' + cm_name.split('.')[5] for cm_name in cm_list])}
                    """
                )
                if category is not None:
                    cm_list = [cm for cm in cm_list if category in cm]
                if freq != "1d":
                    cm_list = [cm for cm in cm_list if freq.lower() in cm]
                cm_name = cm_list[0]
                logger.info(
                    f"""
                    {cm_name.split('.')[3] + '.' + item_name + '.' + cm_name.split('.')[5]} is returned
                    To specify a different cm, use category or freq parameters.
                    For example, .get_df('SP500_EWS', freq = '1M')  \t .get_df('all-mat_cat_rate', category = 'sentiment_exp_us')
                    """
                )
                return cm_name

            return next(
                key.replace("*", item_name)
                for key, items in self.cm_dict.items()
                if item_name in items
            )
        except StopIteration:
            raise ValueError(f"Unknown item_name: {item_name}")

    # Todo: Migrate universe with db or gs sheet or ...
    def determine_base(self):
        def __match_data(u):
            df = self.gs_df
            return list(df[df["Universe"] == u]["Object Path"])

        if self.universe_name == "raw":
            return []
        elif self.universe_name == "kr_stock":
            return __match_data("KR STOCK")
        elif self.universe_name == "us_etf":
            return __match_data("US ETF")
        elif self.universe_name == "us_stock":
            return __match_data("US STOCK")
        elif self.universe_name == "vn_stock":
            return __match_data("VN STOCK")
        elif self.universe_name == "common":
            return __match_data("COMMON")
        else:
            raise ValueError(f"Unknown universe: {self.universe_name}")

    def get_cm_dict(self):
        if self.universe_name == "raw":
            return {}

        api_instance = ContentApi(self.client)
        cm_dict = {}
        for match in self.match_list:
            category = match.split(".")[3]
            try:
                cm_list = api_instance.content_identities_retrieve(
                    category=category
                ).cm_identity_name_list

                net_cm_list = [
                    item.split(".")[4]
                    for item in cm_list
                    if fnmatch.fnmatchcase(item, match)
                ]

                if self.universe_name == "us_etf":
                    net_cm_list = [
                        cm.replace("us-etf-", "")
                        for cm in net_cm_list
                        if "us-etf" in cm
                    ]
                elif self.universe_name == "us_stock":
                    if category in ["price_volume", "classification"]:
                        net_cm_list = [
                            cm.replace("us-stock-", "")
                            for cm in net_cm_list
                            if "us-stock-" in cm
                        ]
                    elif category == "financial":
                        net_cm_list = list(get_data("us_financial")["items"].values)
                elif self.universe_name == "vn_stock":
                    net_cm_list = [
                        cm.replace("vnm-stock-", "")
                        for cm in net_cm_list
                        if "vnm-stock" in cm
                    ]
                cm_dict[match] = net_cm_list
            except Exception as e:
                logger.error(f"API call failed: {e}")
        return cm_dict

    def show(self):
        from IPython.display import HTML, display
        from ipywidgets import interact

        key_mapping = {key.split(".")[3]: key for key in self.cm_dict.keys()}

        def show_key_info(category):
            original_key = key_mapping[category]
            value = self.cm_dict[original_key]

            url = self.gs_df[self.gs_df["Object Path"] == original_key]["URL"].tolist()[
                0
            ]

            scrollable_list = (
                '<div style="height:600px;width:400px;border:1px solid #ccc;overflow:auto;float:left;margin-right:10px;">'
                + "<ul>"
                + "".join(f"<li>{item}</li>" for item in value)
                + "</ul></div>"
            )

            iframe_html = f'<iframe src="{url}" width="1000" height="600" style="float:left;"></iframe>'

            clear_div = '<div style="clear:both;"></div>'

            display(
                HTML(f"<h3>{category}</h3>" + scrollable_list + iframe_html + clear_div)
            )

        simplified_keys = list(key_mapping.keys())

        interact(show_key_info, category=simplified_keys)

    @property
    def item_list(self):
        return sorted(
            set(item for sublist in self.cm_dict.values() for item in sublist)
        )
