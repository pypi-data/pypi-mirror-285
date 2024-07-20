from pydantic import BaseModel

import uuid


class DomainBase(BaseModel):
    """Serves as a base class for all domain models"""
    uid: str = uuid.uuid4().hex