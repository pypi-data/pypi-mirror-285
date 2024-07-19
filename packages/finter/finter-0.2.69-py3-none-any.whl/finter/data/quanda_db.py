import json

import pandas as pd
from finter.api.quanda_db_api import QuandaDbApi
from finter.settings import logger


class DB:
    """
    read only db
    """

    def __init__(self, db_name):
        try:
            self.table_list = QuandaDbApi().quanda_db_table_name_list_retrieve(db=db_name)
        except Exception as e:
            logger.error(f"API call failed: {e}")
            logger.error(f"not supported db: {db_name}")
            raise ValueError(f"not supported db: {db_name}")
        self.table_list = self.table_list['data']
        self.db_name = db_name
        self.column_dict = {}
        self.cache = {}

    def tables(self):
        return self.table_list

    def columns(self, table_name):
        if not self.column_dict.get(table_name):
            data = QuandaDbApi().quanda_db_column_list_retrieve(db=self.db_name, table=table_name)
            self.column_dict[table_name] = data['data']
        return self.column_dict[table_name]

    def query(self, query):
        result = self.cache.get(query)
        if result is None or result.empty:
            data = QuandaDbApi().quanda_db_query_retrieve(db=self.db_name, query=query)
            result = pd.DataFrame(json.loads(data['data']))
            self.cache[query] = result

        return result
