from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Mail(BaseModel):

    to: List[str]
    cc: Optional[List[str]]
    bcc: Optional[List[str]]
    subject: str
    text: str
    html: Optional[str]
    template_id: Optional[str]
    parameters: Optional[Dict[str, Any]]
    meta: Optional[Dict[str, Any]]


class Template(BaseModel):
    template_id: str
    content: str
