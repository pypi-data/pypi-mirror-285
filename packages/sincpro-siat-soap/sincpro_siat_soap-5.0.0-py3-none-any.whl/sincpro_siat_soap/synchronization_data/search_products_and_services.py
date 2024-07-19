from dataclasses import dataclass
from typing import Dict, List, Tuple, TypedDict

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase

from .shared import BaseRequestSynchronization, BaseSIATResponse


@dataclass
class CommandSearchProductsAndServices(BaseRequestSynchronization):
    pass


@dataclass
class ResponseSearchProductsAndServices(BaseSIATResponse):
    pass


class SoapResponse(TypedDict):
    codigoActividad: str
    codigoProducto: str
    descripcionProducto: str
    nandina: str


@feature(CommandSearchProductsAndServices)
class SearchProductsAndServices(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(
        self, param_object: CommandSearchProductsAndServices
    ) -> ResponseSearchProductsAndServices:
        response = self.client.service.sincronizarListaProductosServicios(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )
        comparison_data = self.remove_duplicated_products_and_services(
            response["listaCodigos"]
        )
        return ResponseSearchProductsAndServices(
            raw_response=response, comparison_data=comparison_data
        )

    def remove_duplicated_products_and_services(
        self, code_list: List[SoapResponse]
    ) -> Dict[str, str]:
        response_dict = dict()

        for product in code_list:
            if product["codigoProducto"] not in response_dict.keys():
                # Tuple as key, because python allow
                key = f"({product['codigoProducto']}, {product['codigoActividad']})"
                response_dict[
                    key
                ] = f'{product["codigoActividad"]} - {product["descripcionProducto"]}'

        return response_dict
