from collections import OrderedDict
from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase

from .shared import BaseRequestCommonSyncServices, BaseSIATResponse


@dataclass
class CommandMessageServiceList(BaseRequestCommonSyncServices):
    service: str = "sincronizarListaMensajesServicios"


@dataclass
class CommandSignificantEvents(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaEventosSignificativos"


@dataclass
class CommandReasonCancellation(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaMotivoAnulacion"


@dataclass
class CommandOriginCountry(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaPaisOrigen"


@dataclass
class CommandTypeCI(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoDocumentoIdentidad"


@dataclass
class CommandTypeSectorDocument(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoDocumentoSector"


@dataclass
class CommandTypeEmission(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoEmision"


@dataclass
class CommandTypeRoom(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoHabitacion"


@dataclass
class CommandTypePaymentMethod(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoMetodoPago"


@dataclass
class CommandTypeCurrency(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoMoneda"


@dataclass
class CommandTypePointOfSale(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoPuntoVenta"


@dataclass
class CommandTypeBilling(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTiposFactura"


@dataclass
class CommandTypeUOM(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaUnidadMedida"


@feature(
    [
        CommandMessageServiceList,
        CommandSignificantEvents,
        CommandTypeUOM,
        CommandTypeCurrency,
        CommandOriginCountry,
        CommandTypeEmission,
        CommandReasonCancellation,
        CommandTypeBilling,
        CommandTypeCI,
        CommandTypePaymentMethod,
        CommandTypePointOfSale,
        CommandTypeRoom,
        CommandTypeSectorDocument,
    ]
)
class ExecuteCommonSyncService(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(self, param_object: BaseRequestCommonSyncServices) -> BaseSIATResponse:
        service = getattr(self.client.service, param_object.service)
        response = service(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        response_dict = OrderedDict()
        ordered_list_by_description = sorted(
            response["listaCodigos"], key=lambda x: x["descripcion"]
        )

        for sync in ordered_list_by_description:
            if sync["codigoClasificador"] not in response_dict.keys():
                response_dict[str(sync["codigoClasificador"])] = sync["descripcion"]

        return BaseSIATResponse(raw_response=response, comparison_data=response_dict)
