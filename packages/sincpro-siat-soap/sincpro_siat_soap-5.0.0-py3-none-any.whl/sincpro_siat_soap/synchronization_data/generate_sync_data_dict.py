from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import TypedDict

from sincpro_siat_soap import use_case
from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase
from sincpro_siat_soap.synchronization_data import (
    BaseSIATResponse,
    CommandGetInvoiceLegends,
    CommandGetSectorDocument,
    CommandMessageServiceList,
    CommandOriginCountry,
    CommandReasonCancellation,
    CommandSearchCompanyActivities,
    CommandSearchProductsAndServices,
    CommandSignificantEvents,
    CommandSyncDate,
    CommandTypeBilling,
    CommandTypeCI,
    CommandTypeCurrency,
    CommandTypeEmission,
    CommandTypePaymentMethod,
    CommandTypePointOfSale,
    CommandTypeRoom,
    CommandTypeSectorDocument,
    CommandTypeUOM,
)


@dataclass
class CommandGenerateSyncDataDict:
    nit: int
    cuis: str
    system_code: str
    environment: int = SIAT_ENVIROMENTS.TEST
    point_of_sale: int = 0  # DEFAULT
    branch_office: int = 0  # DEFAULT


class ResponseGenerateSyncDataDict(TypedDict):
    actividades: dict
    productos_y_servicios: dict
    tipos_habitacion: dict
    tipos_documentos: dict
    tipos_punto_venta: dict
    actividades_documento_sector: dict
    leyendas: dict
    eventos_significativos: dict
    mensajes_servicios: dict
    paises: dict
    unidades_de_medida: dict
    tipos_moneda: dict
    tipos_facturas: dict
    tipo_emision: dict
    razon_cancelacion: dict
    tipo_metodo_pago: dict
    tipo_documento_sector: dict


@feature(CommandGenerateSyncDataDict)
class GenerateSyncDataDict(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(self, command: CommandGenerateSyncDataDict) -> ResponseGenerateSyncDataDict:
        commads = self.prepare_command(command)
        self.response: ResponseGenerateSyncDataDict = dict()
        with ThreadPoolExecutor() as executor:
            futures = []
            for c in commads:
                params = c + (self.response,)
                futures.append(executor.submit(self.thread_pool_function, *params))

            for future in as_completed(futures):
                future.result()

        return self.response

    def prepare_command(self, command: CommandGenerateSyncDataDict):
        constructor_dict = {
            "nit": command.nit,
            "cuis": command.cuis,
            "branch_office": command.branch_office,
            "system_code": command.system_code,
            "point_of_sale": command.point_of_sale,
            "environment": command.environment,
        }
        # the second file in the tuple are the keys to map in the dictionary
        commands = [
            (CommandSearchCompanyActivities(**constructor_dict), "actividades"),
            (CommandSearchProductsAndServices(**constructor_dict), "productos_y_servicios"),
            (CommandTypeRoom(**constructor_dict), "tipos_habitacion"),
            (CommandTypeCI(**constructor_dict), "tipos_documentos"),
            (CommandTypePointOfSale(**constructor_dict), "tipos_punto_venta"),
            (CommandGetSectorDocument(**constructor_dict), "actividades_documento_sector"),
            (CommandGetInvoiceLegends(**constructor_dict), "leyendas"),
            (CommandSignificantEvents(**constructor_dict), "eventos_significativos"),
            (CommandMessageServiceList(**constructor_dict), "mensajes_servicios"),
            (CommandOriginCountry(**constructor_dict), "paises"),
            (CommandTypeUOM(**constructor_dict), "unidades_de_medida"),
            (CommandTypeCurrency(**constructor_dict), "tipos_moneda"),
            (CommandTypeBilling(**constructor_dict), "tipos_facturas"),
            (CommandTypeEmission(**constructor_dict), "tipo_emision"),
            (CommandReasonCancellation(**constructor_dict), "razon_cancelacion"),
            (CommandTypePaymentMethod(**constructor_dict), "tipo_metodo_pago"),
            (CommandTypeSectorDocument(**constructor_dict), "tipo_documento_sector"),
        ]
        return commands

    def thread_pool_function(self, command, key, shared_structure_dict):
        response: BaseSIATResponse = use_case.execute(command)
        shared_structure_dict[key] = response.comparison_data
