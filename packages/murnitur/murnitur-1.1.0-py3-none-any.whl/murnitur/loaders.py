import json
import pandas as pd
from typing import Hashable, Any


class Loader:

    def load_csv(path: str) -> list[dict[Hashable, Any]]:
        df = pd.read_csv(path)
        data = df.to_dict(orient="records")
        for item in data:
            if "context" in item and pd.notna(item["context"]):
                item["context"] = [item["context"]]
            if "retrieval_context" in item and pd.notna(item["retrieval_context"]):
                item["retrieval_context"] = [item["retrieval_context"]]

        return data

    def load_json(path: str) -> list[dict[Hashable, Any]]:
        with open(path, "r") as file:
            data_as_dict = json.load(file)

        for item in data_as_dict:
            if "context" in item and isinstance(item["context"], str):
                item["context"] = [item["context"]]
            if "retrieval_context" in item and isinstance(
                item["retrieval_context"], str
            ):
                item["retrieval_context"] = [item["retrieval_context"]]

        return data_as_dict
