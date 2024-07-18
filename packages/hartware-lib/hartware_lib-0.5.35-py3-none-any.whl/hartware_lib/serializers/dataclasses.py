from dataclasses import is_dataclass
from typing import Any

from hartware_lib.serializers.main import NoSerializerMatch
from hartware_lib.types import AnyDict


class DataClassExtraSerializer:
    def __init__(self, *dataclasses: Any):
        self.dataclasses = {dataclass.__name__: dataclass for dataclass in dataclasses}

    def dictify(self, o: Any) -> AnyDict:
        if is_dataclass(o):
            return {"_type": o.__class__.__name__, "value": o.__dict__}

        raise NoSerializerMatch()

    def objectify(self, type: str, dict: Any) -> Any:
        if dataclass := self.dataclasses.get(type):
            return dataclass(**dict)

        raise NoSerializerMatch()
