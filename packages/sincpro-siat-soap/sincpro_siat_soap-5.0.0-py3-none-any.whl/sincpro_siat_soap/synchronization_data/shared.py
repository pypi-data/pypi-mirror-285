from dataclasses import dataclass, field
from typing import Any

from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS


@dataclass
class BaseRequestSynchronization:
    nit: int
    cuis: str
    branch_office: int
    system_code: str
    point_of_sale: int
    environment: int = SIAT_ENVIROMENTS.TEST


class BaseRequestCommonSyncServices(BaseRequestSynchronization):
    service: str


@dataclass
class BaseSIATResponse:
    raw_response: Any = field(repr=False)
    comparison_data: Any
