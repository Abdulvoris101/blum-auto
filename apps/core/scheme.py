from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import json


class Language(str, Enum):
    uz = "uz"
    en = "en"
    ru = "ru"


class UserBase(BaseModel):
    telegramId: int = Field(alias='id')
    firstName: str = Field(alias='first_name')
    lastName: Optional[str] = Field(alias='last_name')
    username: Optional[str]
    referralUsers: List[int] = []
    languageCode: Language = Language.uz
    referredBy: Optional[str] = 'direct'
    isGrantGiven: bool = False
    createdAt: datetime = datetime.now()
    lastUpdated: datetime = datetime.now()


class UserScheme(UserBase):
    id: int

    @field_validator('referralUsers', mode='before')
    @classmethod
    def parse_referral_users(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for referralUsers")
        return v

    def toJson(self, fieldName: str):
        value = getattr(self, fieldName, None)
        return json.dumps(value)

    class Config:
        populate_by_name = True  # Use this to control behavior globally


class UserCreateScheme(UserBase):
    pass


class Farming(BaseModel):
    startTime: int
    endTime: int
    earningsRate: str
    balance: str


class BlumBalanceScheme(BaseModel):
    availableBalance: float
    allPlayPasses: int = Field(alias="playPasses")
    timestamp: int
    farming: Optional[Farming]


class FriendBalanceScheme(BaseModel):
    limitInvitation: str
    usedInvitation: str
    amountForClaim: str
    referralToken: str
    percentFromFriends: int
    percentFromFriendsOfFriends: float
    canClaim: bool
