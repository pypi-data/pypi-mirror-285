from io import StringIO
from typing import Any

from pandas import DataFrame, read_json, Series

from hartware_lib.serializers.main import NoSerializerMatch
from hartware_lib.types import AnyDict


class PandasSerializer:
    def dictify(self, o: Any) -> AnyDict:
        if isinstance(o, DataFrame):
            return {
                "_type": o.__class__.__name__,
                "value": {
                    "data": o.reset_index().to_json(orient="records").encode("utf-8"),
                    "index": o.index.name,
                },
            }
        if isinstance(o, Series):
            return {"_type": o.__class__.__name__, "value": o.to_json().encode("utf-8")}

        raise NoSerializerMatch()

    def objectify(self, type: str, dict: Any) -> DataFrame | Series:
        if type == "DataFrame":
            df = read_json(StringIO(dict["data"].decode("utf-8")), orient="records")

            if dict["index"]:
                df = df.set_index(dict["index"])
            elif not df.empty:
                df = df.set_index("index")
                df.index.name = None

            return df
        if type == "Series":
            return read_json(StringIO(dict.decode("utf-8")), typ="series")

        raise NoSerializerMatch()
