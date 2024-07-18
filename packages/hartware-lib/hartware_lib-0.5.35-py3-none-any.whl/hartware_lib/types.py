from typing import Any, Callable, Dict, Protocol, TypeVar

T = TypeVar("T")

HeadersDict = Dict[str, str]
AnyDict = Dict[str, Any]
Dataclass = TypeVar("Dataclass")

Serializer = Callable[[Any], str]
Deserializer = Callable[[str], Any]


class ExtraSerializer(Protocol):
    def dictify(self, o: Any) -> AnyDict: ...
    def objectify(self, type: str, dict: AnyDict) -> Any: ...
