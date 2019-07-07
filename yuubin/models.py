from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Mail(BaseModel):

    to: List[str]
    cc: List[str]
    bcc: List[str]
    subject: str
    text: str
    html: Optional[str]
    template_id: Optional[str]
    parameters: Dict[str, Any]
    meta: Dict[str, Any]


class Template(BaseModel):
    template_id: str
    content: str
