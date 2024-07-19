from dataclasses import dataclass, field
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
class CommandInvoiceReceptionElectronica:
    nit: int
    cuis: str
    cufd: str
    sector_document: int  # codigoDocumentoSector
    emission_code: int  # codigoEmision
    sent_date: str  # fechaEnvio
    hash_invoice_file: str  # hashArchivoXML No del comprimido
    branch_office: int  # codigoSucursal
    system_code: str  # codigoSistema
    point_of_sell: int  # codigoPuntoVenta
    xml: bytes = field(repr=False)  # archivo
    type_invoice: int
    environment: int = SIAT_ENVIROMENTS.TEST  # codigoAmbiente
    modality: int = SIAT_MODALITY.ELECTRONICA  # codigo Modalidad


@dataclass
class ResponseInvoiceReceptionElectronica:
    reception_code: str
    raw_response: Any


@feature(CommandInvoiceReceptionElectronica)
class InvoiceReceptionRequestSectorEducativo(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SERVICIOS_ELECTRONICA

    def execute(
        self, param_object: CommandInvoiceReceptionElectronica
    ) -> ResponseInvoiceReceptionElectronica:
        response = self.client.service.recepcionFactura(
            SolicitudServicioRecepcionFactura={
                "codigoAmbiente": param_object.environment,
                "codigoDocumentoSector": param_object.sector_document,
                "codigoEmision": param_object.emission_code,
                "codigoModalidad": param_object.modality,
                "codigoPuntoVenta": param_object.point_of_sell,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "tipoFacturaDocumento": param_object.type_invoice,
                # details of invoice
                "archivo": param_object.xml,
                "fechaEnvio": param_object.sent_date,
                "hashArchivo": param_object.hash_invoice_file,
            }
        )

        if response["transaccion"] is False:
            fn = siat_exception_builder(response)
            fn()

        return ResponseInvoiceReceptionElectronica(
            reception_code=response["codigoRecepcion"], raw_response=response
        )
