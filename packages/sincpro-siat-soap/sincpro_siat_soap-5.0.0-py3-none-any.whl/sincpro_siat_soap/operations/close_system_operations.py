from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.logger import logger
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandCloseSystemOperations:
    point_of_sale: int
    system_code: str
    branch_office: int
    cuis: str
    nit: int
    enviroment: int = SIAT_ENVIROMENTS.TEST
    billing_type: int = SIAT_MODALITY.ELECTRONICA


@dataclass
class ResponseCloseSystemOperations:
    raw_response: Any
    success: bool


@feature(CommandCloseSystemOperations)
class CloseSystemOperations(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OPERACIONES

    def execute(
        self, param_object: CommandCloseSystemOperations
    ) -> ResponseCloseSystemOperations:
        logger.info(
            f"The CUIS and CUFD will be revoked for SUCURSAL: [{param_object.branch_office}] PUNTO DE VENTA: [{param_object}]"
        )
        response = self.client.service.cierreOperacionesSistema(
            SolicitudOperaciones={
                "codigoAmbiente": param_object.enviroment,
                "codigoModalidad": param_object.billing_type,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseCloseSystemOperations(
            success=response["transaccion"], raw_response=response
        )
