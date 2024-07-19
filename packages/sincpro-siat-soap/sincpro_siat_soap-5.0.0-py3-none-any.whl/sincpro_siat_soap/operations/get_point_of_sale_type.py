from dataclasses import dataclass
from typing import Any, List

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandGetPointOfSales:
    system_code: str
    branch_office: int
    cuis: str
    nit: int
    enviroment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseGetPointOfSale:
    raw_response: Any
    list_point_of_sales: List[Any]


@feature(CommandGetPointOfSales)
class GetPointOfSales(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OPERACIONES

    def execute(self, param_object: CommandGetPointOfSales) -> ResponseGetPointOfSale:
        response = self.client.service.consultaPuntoVenta(
            SolicitudConsultaPuntoVenta={
                "codigoAmbiente": param_object.enviroment,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseGetPointOfSale(
            list_point_of_sales=response["listaPuntosVentas"], raw_response=response
        )
