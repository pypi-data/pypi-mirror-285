from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra


class NewRequest(BaseModel, extra=Extra.allow):
    demo: Optional[str] = None
    owner: Optional[str] = None
    id: Optional[str] = None
    cloud: Optional[str] = None
    recipePath: Optional[str] = None
    recipeName: Optional[str] = None
    location: Optional[str] = None
    recipeMode: Optional[str] = None
    datacenter: Optional[str] = None
