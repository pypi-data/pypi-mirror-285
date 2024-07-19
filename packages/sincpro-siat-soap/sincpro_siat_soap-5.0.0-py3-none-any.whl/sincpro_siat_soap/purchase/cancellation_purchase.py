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
class CommandRequestPurchaseCancelation:
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int
    control_code: str
    dui_dim_num: str
    invoice_num: int
    customer_nit: int
    environment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponsePurchaseCancelation:
    raw_response: Any


@feature(CommandRequestPurchaseCancelation)
class RequestPurchaseCancelation(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.COMPRAS

    def execute(
        self, param_object: CommandRequestPurchaseCancelation
    ) -> ResponsePurchaseCancelation:
        response = self.client.service.anulacionCompra(
            SolicitudAnulacionCompra={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "codAutorizacion": param_object.control_code,
                "nitProveedor": param_object.customer_nit,
                "nroDuiDim": param_object.dui_dim_num,
                "nroFactura": param_object.invoice_num,
            }
        )

        return ResponsePurchaseCancelation(raw_reponse=response)
