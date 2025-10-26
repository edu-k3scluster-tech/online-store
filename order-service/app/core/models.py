from pydantic import BaseModel
from enum import StrEnum
from datetime import datetime
from decimal import Decimal


class Item(BaseModel):
    id: str
    name: str
    price: Decimal


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class OrderStatusHistory(BaseModel):
    status: OrderStatusEnum
    created_at: datetime


class Order(BaseModel):
    id: str
    user_id: str
    items: list[Item]
    amount: Decimal
    status: OrderStatusEnum
    status_history: list[OrderStatusHistory]
