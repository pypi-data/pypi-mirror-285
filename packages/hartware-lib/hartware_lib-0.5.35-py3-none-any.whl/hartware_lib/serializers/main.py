import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence, Set

from hartware_lib.types import AnyDict, ExtraSerializer


class NoSerializerMatch(Exception):
    pass


def flatten_objects(o: Any, extra_serializers: Set[ExtraSerializer] = ()) -> Any:  # type: ignore[assignment]
    if isinstance(o, dict):
        return {
            k: flatten_objects(v, extra_serializers)
            for k, v in o.items()
        }
    elif isinstance(o, bytes):
        return {"_type": o.__class__.__name__, "value": o.decode("utf-8")}
    elif isinstance(o, list):
        return [flatten_objects(i, extra_serializers) for i in o]
    elif isinstance(o, (bool, float, str, int, type(None))):
        return json.dumps(o)
    elif isinstance(o, (tuple, set)):
        return {"_type": o.__class__.__name__, "value": [flatten_objects(i, extra_serializers) for i in o]}
    elif isinstance(o, datetime):
        return {"_type": o.__class__.__name__, "value": o.isoformat()}
    elif isinstance(o, timedelta):
        return {"_type": o.__class__.__name__, "value": o.total_seconds()}
    elif isinstance(o, Decimal):
        return {"_type": o.__class__.__name__, "value": str(o)}
    elif isinstance(o, Path):
        return {"_type": "Path", "value": str(o)}
    elif extra_serializers:
        for extra_serializer in extra_serializers:
            try:
                return flatten_objects(extra_serializer.dictify(o), extra_serializers)
            except NoSerializerMatch:
                pass

    raise NoSerializerMatch(f"Unknown `{o.__class__.__name__}` type")


def expand_dict(  # noqa: C901
    obj: Any, extra_serializers: Sequence[ExtraSerializer]
) -> Any:
    if isinstance(obj, (bool, int, str, float, type(None))):
        try:
            return json.loads(obj)  # type: ignore[arg-type]
        except json.decoder.JSONDecodeError:
            return obj
    elif isinstance(obj, list):
        return [expand_dict(i, extra_serializers) for i in obj]
    elif isinstance(obj, dict):
        obj_type = obj.get("_type")
        if obj_type is None:
            return {k: expand_dict(v, extra_serializers) for k, v in obj.items()}

        obj_value = obj["value"]

        if obj_type == "bytes":
            return obj_value.encode("utf-8")
        elif obj_type == "datetime":
            return datetime.fromisoformat(obj_value)
        elif obj_type == "timedelta":
            return timedelta(seconds=obj_value)
        elif obj_type == "tuple":
            return tuple([expand_dict(i, extra_serializers) for i in obj_value])
        elif obj_type == "set":
            return set([expand_dict(i, extra_serializers) for i in obj_value])
        elif obj_type == "Decimal":
            return Decimal(obj_value)
        elif obj_type == "Path":
            return Path(obj_value)
        elif extra_serializers:
            obj_type = expand_dict(obj_type, ())
            for extra_serializer in extra_serializers:
                try:
                    return extra_serializer.objectify(
                        obj_type,
                        expand_dict(obj_value, extra_serializers)
                    )
                except NoSerializerMatch:
                    pass

    raise NoSerializerMatch(f"Unknown `{obj_type}` type")


def serialize(
    obj: Any,
    indent: int | None = None,
    extra_serializers: Sequence[ExtraSerializer] = (),
) -> str:
    return json.dumps(flatten_objects(obj, extra_serializers), indent=indent)  # type: ignore[arg-type]


def deserialize(
    obj: str,
    extra_serializers: Sequence[ExtraSerializer] = (),
) -> Any:
    return expand_dict(json.loads(obj), extra_serializers)


@dataclass
class Serializer:
    extra_serializers: Set[ExtraSerializer] = field(default_factory=set)

    def to_dict(self, data: str) -> Any:
        return flatten_objects(data, extra_serializers=self.extra_serializers)

    def to_json(self, data: AnyDict) -> str:
        return serialize(data, extra_serializers=self.extra_serializers)  # type: ignore[arg-type]

    def from_json(self, data: str) -> Any:
        return deserialize(data, extra_serializers=self.extra_serializers)  # type: ignore[arg-type]
