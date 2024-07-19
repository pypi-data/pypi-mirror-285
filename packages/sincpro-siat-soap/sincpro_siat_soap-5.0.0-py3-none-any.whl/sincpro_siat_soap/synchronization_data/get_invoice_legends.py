from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase

from .shared import BaseRequestSynchronization, BaseSIATResponse


@dataclass
class CommandGetInvoiceLegends(BaseRequestSynchronization):
    pass


@dataclass
class ResponseGetInvoiceLegends(BaseSIATResponse):
    pass


@feature(CommandGetInvoiceLegends)
class GetInvoiceLegends(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(self, param_object: CommandGetInvoiceLegends) -> ResponseGetInvoiceLegends:
        response = self.client.service.sincronizarListaLeyendasFactura(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )
        legends = {legend["descripcionLeyenda"] for legend in response["listaLeyendas"]}
        generated_ids = range(len(legends))
        dict_legends = dict(zip(map(str, generated_ids), legends))

        return ResponseGetInvoiceLegends(raw_response=response, comparison_data=dict_legends)
