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
class CommandVerifyNIT:
    nit: int
    nit_para_verificar: int
    cuis: str
    system_code: str
    point_of_sale: int
    branch_office: int
    environment: int = SIAT_ENVIROMENTS.TEST
    billing_type: int = SIAT_MODALITY.ELECTRONICA


@dataclass()
class ResponseVerifyNIT:
    is_valid_nit: bool
    raw_response: Any


@feature(CommandVerifyNIT)
class VerifyNIT(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OBTENCION_CODIGO

    def execute(self, param_object: CommandVerifyNIT) -> ResponseVerifyNIT:
        response = self.client.service.verificarNit(
            SolicitudVerificarNit={
                "codigoAmbiente": param_object.environment,
                "codigoModalidad": param_object.billing_type,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                # 'codigoPuntoVenta': param_object.point_of_sale,
                "nit": param_object.nit,
                "nitParaVerificacion": param_object.nit_para_verificar,
                "cuis": param_object.cuis,
            }
        )
        return ResponseVerifyNIT(is_valid_nit=response["transaccion"], raw_response=response)
