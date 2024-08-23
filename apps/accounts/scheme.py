from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

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
    proxyId: Optional[int]
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
    availablePlayPasses: int = 1
    allPlayPasses: int = 0
    availableBalance: Optional[float] = 0.0
    farmingFreezeHours: int = 0
    needRemind: Optional[bool] = True
    playedGames: Optional[int] = 0
    status: Status = Status.ACTIVE


class BlumAccountScheme(BlumAccountBase):
    id: int


class BlumAccountCreateScheme(BlumAccountBase):
    pass


class ProxyBaseScheme(BaseModel):
    telegramId: Optional[int]
    ip: Optional[str]
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    password: Optional[str]
    type: Optional[str]
    date: Optional[str] = datetime.now()
    dateEnd: Optional[str]


class ProxyDetailScheme(ProxyBaseScheme):
    id: Optional[int]
    proxyId: Optional[str]

class ProxyCreateScheme(ProxyBaseScheme):
    proxyId: Optional[str] = Field(alias="id")


class ProxyDetailJson(BaseModel):
    id: str
    ip: str
    host: str
    port: str
    user: str
    password: str = Field(alias="pass")
    type: str
    date: str
    dateEnd: str = Field(alias="date_end")
    unixtime: int
    unixtime_end: int
    active: str


class ProxyResponseScheme(BaseModel):
    status: str
    userId: str = Field(alias="user_id")
    balance: float
    currency: str
    count: int
    price: float
    period: int
    country: str
    list: Dict[str, ProxyDetailJson]
