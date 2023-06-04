from copy import deepcopy as dc
from typing import List, Union


class JSONCleaner:
    _REMOVED_ATTR_VALUE = "REMOVED"

    @staticmethod
    def _parse_path(path: str) -> List[str]:
        return path.split(".")

    @staticmethod
    def clean_json(
        data: Union[List, dict], attrs_to_remove: List[str]
    ) -> Union[List, dict, str]:
        copied_data = dc(data)
        if not attrs_to_remove:
            return copied_data
        return JSONCleaner._clean(
            copied_data,
            [JSONCleaner._parse_path(x) for x in attrs_to_remove if len(x) > 0],
        )

    @staticmethod
    def _clean(
        data: Union[List, dict], attrs_to_remove: List[List[str]]
    ) -> Union[List, dict, str]:
        for attr_path in attrs_to_remove:
            if len(attr_path) == 0 or attr_path[0] == "*":
                return JSONCleaner._REMOVED_ATTR_VALUE
            if isinstance(data, dict):
                for k in data:
                    if k == attr_path[0]:
                        data[k] = JSONCleaner._clean(dc(data[k]), [attr_path[1:]])
            elif isinstance(data, list):
                for i in range(len(data)):
                    data[i] = JSONCleaner._clean(dc(data[i]), attrs_to_remove)
        return data
