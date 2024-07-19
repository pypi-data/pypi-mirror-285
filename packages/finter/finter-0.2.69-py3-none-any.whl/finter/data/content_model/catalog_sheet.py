import pandas as pd
import requests

from finter.ai.gpt.config import URL_NAME


def get_data(input_str: str = None):
    url = f"http://{URL_NAME}:8282/cm-catalog"
    response = requests.get(url)

    if input_str is not None:
        response = requests.post(url, json={"input": input_str})

    data = response.json()["data"]
    df = pd.DataFrame(data[1:], columns=data[0])
    return df
