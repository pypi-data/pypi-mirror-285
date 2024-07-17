import sys
from typing import List

from launchflow.cli.utils import import_from_string
from launchflow.service import Service


def import_services(service_import_strs: str) -> List[Service]:
    sys.path.insert(0, "")
    services: List[Service] = []
    for service_str in service_import_strs:
        imported_service = import_from_string(service_str)
        if not isinstance(imported_service, Service):
            raise ValueError(f"Service {imported_service} is not a valid Service")
        services.append(imported_service)
    return services
