import re
from typing import TYPE_CHECKING, Any, Dict, cast

from .strategies import NativeProperties, Properties

if TYPE_CHECKING:
    from .adapter import Adapter


class WeightCalculator:
    def __init__(self, adapter: "Adapter"):
        self.adapter = adapter
        self.cache: Dict[str, Any] = {}
        self.native_properties_cache: Dict[str, Any] = {}
        self.properties_cache: Dict[str, Any] = {}

    def cached(self, name: str) -> Any:
        if name in self.cache:
            return self.cache[name]

        if hasattr(self.adapter, name):
            self.cache[name] = getattr(self.adapter, name)
        else:
            self.cache[name] = None

        return self.cache[name]

    def properties_cached(self, name: str) -> Any:
        if name in self.properties_cache:
            return self.properties_cache[name]

        if Properties.strategy_name in self.adapter.supported_strategies:
            self.properties_cache[name] = self.adapter.get_strategy(Properties).get_property_value(name)
        else:
            self.properties_cache[name] = None

        return self.properties_cache[name]

    def native_properties_cached(self, name: str) -> Any:
        if name in self.native_properties_cache:
            return self.native_properties_cache[name]

        if NativeProperties.strategy_name in self.adapter.supported_strategies:
            self.native_properties_cache[name] = self.adapter.get_strategy(NativeProperties).get_native_property_value(
                name
            )
        else:
            self.native_properties_cache[name] = None

        return self.native_properties_cache[name]

    @staticmethod
    def test_values(actual: Any, expected: Any) -> bool:
        if isinstance(expected, re.Pattern):
            return expected.fullmatch(str(actual)) is not None

        return bool(actual == expected)

    def calculate(self, criterias: Dict[str, object]) -> int:
        weight = 0

        if "technology" in criterias and criterias["technology"] is not None:
            if self.test_values(type(self.adapter.technology), criterias["technology"]):
                weight += 100000
            else:
                return 0

        if "role" in criterias and criterias["role"] is not None:
            if self.cached("role") == criterias["role"]:
                weight += 10000
            else:
                try:
                    i = list(self.cached("supported_roles")).index(criterias["role"])
                    weight += 5000 - i
                except ValueError:
                    return 0

        if "framework_id" in criterias and criterias["framework_id"] is not None:
            if self.test_values(self.cached("framework_id"), criterias["framework_id"]):
                weight += 1000
            else:
                return 0

        if "class_name" in criterias and criterias["class_name"] is not None:
            if self.test_values(self.cached("class_name"), criterias["class_name"]):
                weight += 500
            else:
                return 0

        if "tag_name" in criterias and criterias["tag_name"] is not None:
            if self.test_values(self.cached("tag_name"), criterias["tag_name"]):
                weight += 400
            else:
                return 0

        if "properties" in criterias and criterias["properties"] is not None:
            for p, v in cast(Dict[str, Any], criterias["properties"]).items():
                if self.test_values(self.properties_cached(p), v):
                    weight += 200
                else:
                    return 0

        if "native_properties" in criterias and criterias["native_properties"] is not None:
            for p, v in cast(Dict[str, Any], criterias["native_properties"]).items():
                if self.test_values(self.native_properties_cached(p), v):
                    weight += 200
                else:
                    return 0

        return weight
