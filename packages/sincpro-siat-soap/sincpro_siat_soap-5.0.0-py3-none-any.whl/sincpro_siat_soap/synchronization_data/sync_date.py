from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_MODALITY, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase

from .shared import BaseRequestSynchronization, BaseSIATResponse


@dataclass
class CommandSyncDate(BaseRequestSynchronization):
    pass


@dataclass
class ResponseSyncDate(BaseSIATResponse):
    pass


@feature(CommandSyncDate)
class SyncDate(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(self, param_object: CommandSyncDate) -> ResponseSyncDate:
        response = self.client.service.sincronizarFechaHora(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "codigoPuntoVenta": param_object.point_of_sale,
                "nit": param_object.nit,
                "cuis": param_object.cuis,
            }
        )

        return ResponseSyncDate(raw_response=response, comparison_data=response["fechaHora"])
