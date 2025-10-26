from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.models import Order
from app.application.container import ApplicationContainer

from app.application.create_order import CreateOrderUseCase, OrderDTO

router = APIRouter()


class OrderCreateRequest(OrderDTO):
    pass


class OrderResponseModel(Order):
    pass


@router.post(
    "/orders",
    status_code=HTTPStatus.CREATED,
    response_model=OrderResponseModel,
)
@inject
async def create_bulk_transfer(
    order: OrderCreateRequest,
    create_order_use_case: CreateOrderUseCase = Depends(
        Provide[ApplicationContainer.create_order_use_case]
    ),
):
    try:
        return await create_order_use_case(
            order=order
        )
    except Exception as e:
        return JSONResponse(
            content={"message": "Internal server error while processing bulk transfer"},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
