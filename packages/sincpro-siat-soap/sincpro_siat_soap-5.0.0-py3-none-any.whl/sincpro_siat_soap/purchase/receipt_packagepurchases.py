from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandReceiptPackagePurchases:
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int
    xml: bytes
    quantity_invoices: int
    date: datetime
    management: int
    invoice_hash: str
    period: int
    environment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseCommandReceiptPackagePurchases:
    raw_response: Any
    # success: bool


@feature(CommandReceiptPackagePurchases)
class RequestCommandReceiptPackagePurchases(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.COMPRAS

    def execute(
        self, param_object: CommandReceiptPackagePurchases
    ) -> ResponseCommandReceiptPackagePurchases:
        response = self.client.service.recepcionPaqueteCompras(
            SolicitudRecepcionCompras={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "archivo": param_object.xml,
                "cantidadFacturas": param_object.quantity_invoices,
                "fechaEnvio": param_object.date,
                "gestion": param_object.management,
                "hashArchivo": param_object.invoice_hash,
                "periodo": param_object.period,
            }
        )

        return ResponseCommandReceiptPackagePurchases(raw_response=response)
