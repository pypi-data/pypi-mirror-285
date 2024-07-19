from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandGetRegisteredSignificantEvents:
    point_of_sale: int
    system_code: str
    branch_office: int
    event_date: str
    cufd: str
    cuis: str
    nit: int
    enviroment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseGetRegisteredSignificantEvents:
    raw_response: Any
    # list_point_of_sales: List[Any]


@feature(CommandGetRegisteredSignificantEvents)
class GetRegisteredSignificantEvents(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OPERACIONES

    def execute(
        self, param_object: CommandGetRegisteredSignificantEvents
    ) -> ResponseGetRegisteredSignificantEvents:
        response = self.client.service.consultaEventoSignificativo(
            SolicitudConsultaEvento={
                "codigoAmbiente": param_object.enviroment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "fechaEvento": param_object.event_date,
            }
        )

        return ResponseGetRegisteredSignificantEvents(raw_response=response)
