from typing import Optional

from ..core.base import BaseModel


class Role(BaseModel):
    name: str
    description: Optional[str]
    is_active: bool = True
