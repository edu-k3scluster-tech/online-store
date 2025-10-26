from decimal import Decimal

from pydantic import BaseModel

from app.core.models import Item, OrderStatusEnum
from app.infrastructure.repositories import OrderRepository
from app.infrastructure.unit_of_work import UnitOfWork


class OrderDTO(BaseModel):
    user_id: str
    items: list[Item]


class CreateOrderUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ):
        self._unit_of_work = unit_of_work

    async def __call__(self, order: OrderDTO) -> None:
        async with self._unit_of_work() as uow:
            amount = sum((item.price for item in order.items), start=Decimal("0"))
            order = await uow.orders.create(
                order=OrderRepository.CreateDTO(
                    user_id=order.user_id,
                    items=order.items,
                    amount=amount,
                    status=OrderStatusEnum.NEW,
                )
            )
            await uow.commit()
            return order
