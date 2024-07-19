from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandRequestConsultPurchases:
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int
    date: datetime
    environment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseConsultPurchase:
    raw_response: Any
    # success: bool


@feature(CommandRequestConsultPurchases)
class RequestConsultPurchases(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.COMPRAS

    def execute(
        self, param_object: CommandRequestConsultPurchases
    ) -> ResponseConsultPurchase:
        response = self.client.service.consultaCompras(
            SolicitudConsultaCompras={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "fecha": param_object.date,
            }
        )

        return ResponseConsultPurchase(raw_response=response)
