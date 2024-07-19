from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase

from .shared import BaseRequestSynchronization, BaseSIATResponse


@dataclass
class CommandGetSectorDocument(BaseRequestSynchronization):
    pass


@dataclass
class ResponseGetSectorDocument(BaseSIATResponse):
    pass


@feature(CommandGetSectorDocument)
class GetSectorDocument(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(self, param_object: CommandGetSectorDocument) -> ResponseGetSectorDocument:
        response = self.client.service.sincronizarListaActividadesDocumentoSector(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        response_dict = dict()
        for sector_document in response["listaActividadesDocumentoSector"]:
            if sector_document["codigoDocumentoSector"] not in response_dict.keys():
                response_dict[
                    str(sector_document["codigoDocumentoSector"])
                ] = sector_document["tipoDocumentoSector"]

        return ResponseGetSectorDocument(raw_response=response, comparison_data=response_dict)
