from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from schematics import Model
from schematics.types import DictType, ListType, StringType


class DataclassModel(Model):
    def __init__(self, _dict=None, context=None, **kwargs):
        if _dict is not None:
            _dict.update(kwargs)
            super().__init__(_dict, context=context)
        else:
            super().__init__(kwargs, context=context)


@dataclass(init=False)
class Mail(DataclassModel):

    to: List[str] = ListType(StringType)
    cc: List[str] = ListType(StringType, required=False, default=[])
    bcc: List[str] = ListType(StringType, required=False, default=[])
    subject: str = StringType()
    text: str = StringType()
    html: Optional[str] = StringType(required=False, default=None)
    template_id: Optional[str] = StringType(required=False, default=None)
    parameters: Dict[str, Any] = DictType(StringType, required=False, default={})
    meta: Dict[str, Any] = DictType(StringType, required=False, default={})


@dataclass(init=False)
class Template(DataclassModel):
    template_id: str = StringType(max_length=255)
    content: str = StringType()
