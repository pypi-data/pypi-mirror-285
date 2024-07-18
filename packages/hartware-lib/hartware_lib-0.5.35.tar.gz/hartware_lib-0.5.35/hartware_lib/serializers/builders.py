from __future__ import annotations

from typing import Any, Set

from hartware_lib.serializers.dataclasses import DataClassExtraSerializer
from hartware_lib.serializers.main import Serializer

try:
    from hartware_lib.serializers.pandas import PandasSerializer
except ModuleNotFoundError:
    pass

from hartware_lib.types import ExtraSerializer


class SerializerBuilder:
    def __init__(self) -> None:
        self.extra_serializers: Set[ExtraSerializer] = set()

    def add_serializer(self, extra_serializer: ExtraSerializer) -> SerializerBuilder:
        self.extra_serializers.add(extra_serializer)

        return self

    def with_pandas(self) -> SerializerBuilder:
        try:
            return self.add_serializer(PandasSerializer())
        except NameError:
            raise Exception("Pandas needs to be installed")

    def with_dataclasses(self, *dataclasses: Any) -> SerializerBuilder:
        return self.add_serializer(DataClassExtraSerializer(*dataclasses))

    def get(self) -> Serializer:
        return Serializer(self.extra_serializers)
