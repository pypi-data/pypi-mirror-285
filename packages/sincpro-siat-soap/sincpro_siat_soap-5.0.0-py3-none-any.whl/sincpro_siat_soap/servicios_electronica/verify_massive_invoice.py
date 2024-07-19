from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandVerifyMassiveInvoiceElectronic:
    document_type: int
    emission_code: int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int
    invoice_type: int
    reception_code: str
    modality: int = SIAT_MODALITY.ELECTRONICA
    environment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseVerifyMassiveInvoiceElectronic:
    reception_code: str
    raw_response: dict


@feature(CommandVerifyMassiveInvoiceElectronic)
class VerifyMassiveInvoiceSiatElectronic(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SERVICIOS_ELECTRONICA

    def execute(
        self, param_object: CommandVerifyMassiveInvoiceElectronic
    ) -> ResponseVerifyMassiveInvoiceElectronic:
        response = self.client.service.validacionRecepcionMasivaFactura(
            SolicitudServicioValidacionRecepcionMasiva={
                "codigoAmbiente": param_object.environment,
                "codigoDocumentoSector": param_object.document_type,
                "codigoEmision": param_object.emission_code,
                "codigoModalidad": param_object.modality,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "tipoFacturaDocumento": param_object.invoice_type,
                "codigoRecepcion": param_object.reception_code,
            }
        )

        if response["transaccion"] is False:
            fn = siat_exception_builder(response)
            fn()

        return ResponseVerifyMassiveInvoiceElectronic(
            response["codigoRecepcion"], raw_response=response
        )
