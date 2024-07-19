from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.UseCase import UseCase


class POINT_OF_SALE_TYPES:
    COMISIONISTA = 1
    VENTANILLA_COBRANZA = 2
    MOVILES = 3
    YPFB = 4
    VENTA_CAJERO = 5


@dataclass
class CommandCreatePointOfSale:
    type_point_of_sale: int
    description: str
    point_of_sale_name: str
    system_code: str
    branch_office: int
    cuis: str
    nit: int
    enviroment: int = SIAT_ENVIROMENTS.TEST
    billing_type: int = SIAT_MODALITY.ELECTRONICA


@dataclass
class ResponseCreatePointOfSale:
    raw_response: Any
    point_of_sale_id: int


@feature(CommandCreatePointOfSale)
class CreatePointOfSale(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OPERACIONES

    def execute(self, param_object: CommandCreatePointOfSale) -> ResponseCreatePointOfSale:
        response = self.client.service.registroPuntoVenta(
            SolicitudRegistroPuntoVenta={
                "nombrePuntoVenta": param_object.point_of_sale_name,
                "descripcion": param_object.description,
                "codigoAmbiente": param_object.enviroment,
                "codigoModalidad": param_object.billing_type,
                "codigoTipoPuntoVenta": param_object.type_point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseCreatePointOfSale(
            point_of_sale_id=response["codigoPuntoVenta"], raw_response=response
        )
