from typing import List, Optional

import pydantic

PYDANTIC_V2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic.v1 import BaseModel
else:
    from pydantic import BaseModel

from typing import List

from scale_egp.utils.model_utils import BaseModel


class Account(BaseModel):
    id: str
    name: str


class UserRole(BaseModel):
    role: str
    account: Account


class UserInfoResponse(BaseModel):
    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    accounts: List[UserRole]
