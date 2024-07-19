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
class CommandGenerateCUIS:
    nit: int
    system_code: str
    point_of_sale: int
    branch_office: int
    environment: int = SIAT_ENVIROMENTS.TEST
    billing_type: int = SIAT_MODALITY.ELECTRONICA


@dataclass()
class ResponseGenerateCUIS:
    cuis: str
    raw_response: Any


@feature(CommandGenerateCUIS)
class GenerateCUIS(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OBTENCION_CODIGO

    def execute(self, param_object: CommandGenerateCUIS) -> ResponseGenerateCUIS:
        response = self.client.service.cuis(
            SolicitudCuis={
                "codigoAmbiente": param_object.environment,
                "codigoModalidad": param_object.billing_type,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "codigoPuntoVenta": param_object.point_of_sale,
                "nit": param_object.nit,
            }
        )
        return ResponseGenerateCUIS(raw_response=response, cuis=response["codigo"])
