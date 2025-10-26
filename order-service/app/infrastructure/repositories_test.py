import uuid
from decimal import Decimal
import pytest
from unittest.mock import ANY
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Order, Item, OrderStatusEnum, OrderStatusHistory
from app.infrastructure.repositories import OrderRepository


@pytest.fixture
async def order_repo(session: AsyncSession) -> OrderRepository:
    return OrderRepository(session)


class TestOrderRepository:
    @pytest.mark.asyncio
    async def test_create_order(
        self, order_repo: OrderRepository, item_factory
    ):
        # Given
        items = [item_factory() for _ in range(3)]
        user_id = str(uuid.uuid4())

        # When
        order_new = await order_repo.create(
            OrderRepository.CreateDTO(
                user_id=user_id,
                items=items,
                amount=sum(item.price for item in items),
                status=OrderStatusEnum.NEW
            )
        )

        # Then
        assert isinstance(order_new, Order)
        assert order_new.user_id == user_id
        assert order_new.items == items
        assert order_new.amount == Decimal('31.50')
        assert order_new.status == OrderStatusEnum.NEW
        assert [s.status for s in order_new.status_history] == [OrderStatusEnum.NEW]
