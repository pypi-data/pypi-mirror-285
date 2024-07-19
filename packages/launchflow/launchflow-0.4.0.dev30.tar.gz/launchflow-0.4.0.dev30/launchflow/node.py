import dataclasses
from enum import Enum
from typing import Any, Dict, Optional


def _serialize_type(val: Any) -> Any:
    if dataclasses.is_dataclass(val):
        return dataclasses.asdict(val)
    elif isinstance(val, Enum):
        return val.value
    elif isinstance(val, list):
        return [_serialize_type(i) for i in val]
    elif isinstance(val, bool):
        return str(val).lower()
    elif val is None:
        return None
    return val


def _json_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    to_ret = {}
    for key, val in d.items():
        val = _serialize_type(val)
        if val is not None:
            to_ret[key] = _serialize_type(val)
    return to_ret


@dataclasses.dataclass
class Inputs:
    def to_dict(self) -> Dict[str, Any]:
        return _json_dict(dataclasses.asdict(self))


@dataclasses.dataclass
class Outputs:
    gcp_id: Optional[str] = dataclasses.field(default=None, init=False)
    aws_arn: Optional[str] = dataclasses.field(default=None, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return _json_dict(dataclasses.asdict(self))


class Node:
    def inputs(self) -> Inputs:
        raise NotImplementedError

    async def inputs_async(self) -> Inputs:
        raise NotImplementedError

    def outputs(self) -> Outputs:
        raise NotImplementedError

    async def outputs_async(self) -> Outputs:
        raise NotImplementedError
