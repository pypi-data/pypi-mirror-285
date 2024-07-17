from pih.consts import CONST
from pih.consts.service_roles import ServiceRoles
from pih.tools import NetworkTool, OSTool, j, e, n, ne
from pih.consts.service import EVENT_LISTENER_NAME_PREFIX, SUPPORT_NAME_PREFIX
from pih.collections.service import (
    ServiceDescriptionBase,
    ServiceInformation,
    ServiceDescription,
)


from enum import Enum


class ServiceTool:

    @staticmethod
    def is_service_as_listener(description: ServiceDescriptionBase) -> bool:
        return description.name.find(EVENT_LISTENER_NAME_PREFIX) == 0

    @staticmethod
    def is_service_as_support(description: ServiceDescriptionBase) -> bool:
        return description.name.find(SUPPORT_NAME_PREFIX) == 0


class ServiceAdminTool:

    service_collection: dict[ServiceDescriptionBase, ServiceInformation] = {}

    @staticmethod
    def remove_service_from_service_collection(value: ServiceDescriptionBase) -> None:
        if value in ServiceAdminTool.service_collection:
            del ServiceAdminTool.service_collection[value]

    @staticmethod
    def clear_service_collection() -> None:
        ServiceAdminTool.service_collection = {}

    @staticmethod
    def get_service_collection() -> dict[ServiceDescriptionBase, ServiceInformation]:
        return ServiceAdminTool.service_collection

    @staticmethod
    def update_service_information(
        value: ServiceDescriptionBase | list[ServiceDescriptionBase],
        add: bool = True,
        overwrite: bool = False,
    ) -> None:
        if not isinstance(value, list):
            value = [value]
        if overwrite:
            if ne(value):
                ServiceAdminTool.service_collection = {}
        for item in value:
            if add:
                ServiceAdminTool.service_collection[item] = item
            else:
                if item in ServiceAdminTool.service_collection:
                    del ServiceAdminTool.service_collection[item]

    @staticmethod
    def create_port(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> int:
        return (
            ServiceRoleTool.service_description(service_role_or_description).port
            or NetworkTool.next_free_port()
        )

    @staticmethod
    def create_host(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> str:
        description: ServiceDescription = ServiceRoleTool.service_description(
            service_role_or_description
        )
        return (
            OSTool.host()
            if description.isolated or e(description.host)
            else description.host
        )


class ServiceRoleTool:

    @staticmethod
    def service_description(
        value: Enum | str | ServiceDescriptionBase, get_source_description: bool = False
    ) -> ServiceDescriptionBase | None:
        def isolated_name(
            value: ServiceDescriptionBase | None,
        ) -> ServiceDescriptionBase | None:
            if n(value):
                return None
            value.name = (
                j((CONST.ISOLATED_ARG_NAME, value.name), CONST.SPLITTER)
                if value.isolated and value.name.find(CONST.ISOLATED_ARG_NAME) == -1
                else value.name
            )
            return value

        if isinstance(value, str):
            for service_role in ServiceRoles:
                if ServiceRoleTool.service_description(service_role).name == value:
                    return isolated_name(service_role.value)
            return None
        if isinstance(value, ServiceDescriptionBase):
            return isolated_name(
                ServiceRoleTool.service_description(value.name)
                if get_source_description
                else value
            )
        return isolated_name(value.value)
