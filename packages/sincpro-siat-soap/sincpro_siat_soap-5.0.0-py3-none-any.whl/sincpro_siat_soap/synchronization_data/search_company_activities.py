from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase

from .shared import BaseRequestSynchronization, BaseSIATResponse


@dataclass
class CommandSearchCompanyActivities(BaseRequestSynchronization):
    pass


@dataclass
class ResponseSearchCompanyActivities(BaseSIATResponse):
    pass


@feature(CommandSearchCompanyActivities)
class SearchCompanyActivities(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(
        self, param_object: CommandSearchCompanyActivities
    ) -> ResponseSearchCompanyActivities:
        response = self.client.service.sincronizarActividades(
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

        for activity in response["listaActividades"]:
            if activity["codigoCaeb"] not in response_dict.keys():
                response_dict[activity["codigoCaeb"]] = activity["descripcion"]

        return ResponseSearchCompanyActivities(
            raw_response=response, comparison_data=response_dict
        )
