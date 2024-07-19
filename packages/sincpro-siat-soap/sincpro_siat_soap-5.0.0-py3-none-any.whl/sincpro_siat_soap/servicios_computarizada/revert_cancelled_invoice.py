from dataclasses import dataclass
from typing import Literal

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass(kw_only=True)
class CommandRevertCancelledInvoiceComputarizada:
    sector_document: int
    emission_code: int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int
    invoice_type: int
    cuf: str
    modality: SIAT_MODALITY.ELECTRONICA
    environment: SIAT_ENVIROMENTS.TEST


type_verified_status = Literal[
    "RECHAZADA", "OBSERVADA", "VALIDA", "ANULADA", "REVERSION DE ANULACION CONFIRMADA"
]


@dataclass
class ResponseRevertCancelledInvoiceComputarizada:
    reception_code: str
    literal_status: type_verified_status
    raw_response: dict


@feature(CommandRevertCancelledInvoiceComputarizada)
class RevertCancelledInvoiceComputarizada(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SERVICIOS_COMPUTARIZADA

    def execute(
        self, param_object: CommandRevertCancelledInvoiceComputarizada
    ) -> ResponseRevertCancelledInvoiceComputarizada:
        response = self.client.service.reversionAnulacionFactura(
            SolicitudServicioReversionAnulacionFactura={
                "codigoAmbiente": param_object.environment,
                "codigoDocumentoSector": param_object.sector_document,
                "codigoEmision": param_object.emission_code,
                "codigoModalidad": param_object.modality,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "tipoFacturaDocumento": param_object.invoice_type,
                "cuf": param_object.cuf,
            }
        )

        return ResponseRevertCancelledInvoiceComputarizada(
            reception_code=response["codigoRecepcion"],
            literal_status=response["codigoDescripcion"],
            raw_response=response,
        )
