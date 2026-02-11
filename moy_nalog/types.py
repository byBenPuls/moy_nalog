from typing import Union, Optional
from dataclasses import dataclass
from datetime import datetime

from moy_nalog.constants import CancelType


@dataclass
class Token:
    value: str
    expire_in: datetime
    refresh_value: Optional[str] = None


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class SmsChallenge:
    challenge_token: str
    expire_date: str
    expire_in: int


@dataclass
class AuthDetails:
    inn: str
    token: Token


@dataclass
class Income:
    id: str
    approved_receipt_uuid: str
    json_url: str
    print_url: str

    data: Optional[dict] = None


@dataclass
class CancellationInfo:
    operation_time: datetime
    register_time: datetime
    tax_period_id: int
    comment: CancelType


@dataclass
class CanceledIncome:
    id: str
    name: str
    operation_time: datetime
    request_time: datetime
    payment_type: str  # TODO: CASH etc
    partner_code: Optional[str]  # TODO: hz
    total_amount: Union[int, float]
    cancellation_info: CancellationInfo
    source_device_id: str


@dataclass
class User:
    last_name: Optional[str]
    id: Optional[int]
    display_name: Optional[str]
    middle_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    inn: Optional[str]
    snils: Optional[str]
    avatar_exists: Optional[bool]
    initial_registration_date: Optional[datetime]
    registration_date: Optional[datetime]
    first_receipt_register_time: Optional[datetime]
    first_receipt_cancel_time: Optional[datetime]
    hide_cancelled_receipt: Optional[bool]
    register_available: Optional[str]
    status: Optional[str]
    restricted_mode: Optional[bool]
    pfr_url: Optional[str]
    login: Optional[str]
