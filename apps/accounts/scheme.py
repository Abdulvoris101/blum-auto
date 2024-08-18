from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator
import json


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AccountBase(BaseModel):
    telegramId: int
    userId: int
    phoneNumber: str
    sessionName: str
    status: Status = Status.ACTIVE
    createdAt: datetime = datetime.now()


class AccountScheme(AccountBase):
    id: int
    lastUpdated: datetime

    def toJson(self, fieldName: str):
        value = getattr(self, fieldName, None)
        return json.dumps(value)

    class Config:
        populate_by_name = True  # Use this to control behavior globally


class AccountCreateScheme(AccountBase):
    pass


class AccountGetScheme(AccountBase):
    pass


class BlumAccountBase(BaseModel):
    accountId: int
    availablePlayPasses: int = 0
    allPlayPasses: int = 0
    availableBalance: Optional[float] = 0.0
    farmingFreezeHours: int = 0
    needRemind: Optional[bool] = True
    status: Status = Status.ACTIVE


class BlumAccountScheme(BlumAccountBase):
    id: int


class BlumAccountCreateScheme(BlumAccountBase):
    pass

