from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandCancellationCreditDebit:
    nit: int
    cuis: str
    cufd: str
    cuf: str
    sector_document: int  # codigoDocumentoSector
    emission_code: int  # codigoEmision
    branch_office: int  # codigoSucursal
    system_code: str  # codigoSistema
    point_of_sale: int  # codigoPuntoVenta
    cancellation_reason: int
    type_invoice: int
    environment: int = SIAT_ENVIROMENTS.TEST  # codigoAmbiente
    modality: int = SIAT_MODALITY.ELECTRONICA  # codigo Modalidad


@dataclass
class ResponseCancellationCreditDebit:
    transaction: bool
    raw_response: Any


@feature(CommandCancellationCreditDebit)
class CancellationCreditDebit(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.NOTA_DE_CREDITO

    def execute(
        self, param_object: CommandCancellationCreditDebit
    ) -> ResponseCancellationCreditDebit:
        response = self.client.service.anulacionDocumentoAjuste(
            SolicitudServicioAnulacionDocumentoAjuste={
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
                "tipoFacturaDocumento": param_object.type_invoice,
                "codigoMotivo": param_object.cancellation_reason,
                "cuf": param_object.cuf,
            }
        )

        if response["transaccion"] is False:
            fn = siat_exception_builder(response)
            fn()

        return ResponseCancellationCreditDebit(
            transaction=response["transaccion"], raw_response=response
        )
