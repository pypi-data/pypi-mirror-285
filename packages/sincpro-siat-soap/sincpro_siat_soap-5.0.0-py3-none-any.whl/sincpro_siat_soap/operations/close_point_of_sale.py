from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandClosePointOfSale:
    point_of_sale: int
    system_code: str
    branch_office: int
    cuis: str
    nit: int
    enviroment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseClosePointOfSale:
    raw_response: Any
    success: bool


@feature(CommandClosePointOfSale)
class ClosePointOfSale(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OPERACIONES

    def execute(self, param_object: CommandClosePointOfSale) -> ResponseClosePointOfSale:
        response = self.client.service.cierrePuntoVenta(
            SolicitudCierrePuntoVenta={
                "codigoAmbiente": param_object.enviroment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseClosePointOfSale(
            success=response["transaccion"], raw_response=response
        )
