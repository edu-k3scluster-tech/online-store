from dependency_injector import containers, providers

from app.application.create_order import CreateOrderUseCase
from app.infrastructure.container import InfrastructureContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    infrastructure_container = providers.Container[InfrastructureContainer](
        InfrastructureContainer,
        config=config.infrastructure,
    )

    create_order_use_case = providers.Singleton[CreateOrderUseCase](
        CreateOrderUseCase, unit_of_work=infrastructure_container.unit_of_work
    )
