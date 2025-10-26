from sqlalchemy import (
    Column,
    MetaData,
    Table, Integer, Text, ForeignKey, DECIMAL, UUID, JSON, DateTime, func
)
import uuid

metadata = MetaData()

orders_tbl = Table(
    "orders",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", Text, nullable=False),
    Column("items", JSON, nullable=False),
    Column("amount", DECIMAL(10, 2), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

order_statuses_tbl = Table(
    "order_statuses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", UUID(as_uuid=True), ForeignKey("orders.id")),
    Column("status", Text, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

