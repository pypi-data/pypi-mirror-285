from typing import TypedDict, Any, Dict, List, Optional, Literal, Tuple, Union, cast
from .typing import Service
from .utils import is_valid_uuid
from .exceptions import RetryException, AbortException

import datetime

def parse_iso_format(iso: str):
    iso_without_z = iso.rstrip("Z")
    return datetime.datetime.fromisoformat(iso_without_z).replace(tzinfo=datetime.timezone.utc)

class ServiceMeta(Service):
    execution_data: Union[None, datetime.datetime]

class TenantContext(TypedDict, total=True):
    name: str

class Context(TypedDict, total=True):
    input: Any
    meta: Any
    tenant: TenantContext
    data: Dict[str, Any]
    dates: Dict[str, str]
    errors: Dict[str, Any]

class ContextHelper:
    def __init__(self, id: str, context: Context, serviceList: List[Service]):
        self.__context = context
        self.__serviceList = serviceList
        self.__id = id

    def retry(self, delay: Optional[int] = None):
        raise RetryException(delay)

    def abort(self, reason: Optional[str] = ''):
        raise AbortException(reason)

    def __get_service_ids(self, service_identifier: str):
        if (is_valid_uuid(service_identifier)):
            return [service_identifier]

        return [service['id'] for service in self.__serviceList if service.get('alias') == service_identifier or service.get('name') == service_identifier]

    def __get_from_context(self, field: Literal["data", "errors"], service_identifier: str) -> list[Tuple[Any, datetime.datetime]]:
        service_ids = self.__get_service_ids(service_identifier)

        service_ids = self.__get_service_ids(service_identifier)
        results = []
        for service_id in service_ids:
            if service_id in self.__context[field]:
                results.append(
                    (
                        self.__context[field][service_id],
                        parse_iso_format(self.__context["dates"][service_id])
                    )
                )
        return results

    def get_input(self):
        return self.__context["input"]

    def get_tenant_name(self):
        return self.__context["tenant"]["name"]

    def get_meta(self):
        return self.__context["meta"]

    def get_configuration(self):
        meta = self.get_service_meta(self.__id)
        if (not meta):
            return None
        return meta["configuration"]

    def get_service_meta(self, service_identifier: str):
        service_id = self.__get_service_ids(service_identifier)[0]
        if (not service_id):
            return None

        service = next((service for service in self.__serviceList if service['id'] == service_id), None)
        if (not service):
            return None

        execution_date = parse_iso_format(self.__context['dates'][service_id]) if service_id in self.__context['dates'] else None

        return cast(ServiceMeta, {
            **service,
            "executionDate": execution_date,
        })

    def get_results(self):
        return [
            {
                **service,
                "executionDate": parse_iso_format(self.__context['dates'][service['id']]) if service['id'] in self.__context['dates'] else None,
                "data": self.__context['data'].get(service['id']),
                "error": self.__context['errors'].get(service['id']),
            }
            for service in self.__serviceList
        ]

    def get_last_service_data(self, service_identifier: str):
        data_with_dates = self.__get_from_context('data', service_identifier)
        data_with_dates.sort(key=lambda x: x[1], reverse=True)
        return data_with_dates[0][0] if data_with_dates else None

    def get_service_data(self, service_identifier: str):
        return self.__get_from_context('data', service_identifier)[0][0] or None

    def get_last_service_error(self, service_identifier: str):
        data_with_dates = self.__get_from_context('errors', service_identifier)
        data_with_dates.sort(key=lambda x: x[1], reverse=True)
        return data_with_dates[0][0] if data_with_dates else None

    def get_service_error(self, service_identifier: str):
        return self.__get_from_context('errors', service_identifier)[0][0] or None
