from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.digital_files.infrastructure.util_format import (
    datetime_for_send_invoice,
)
from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandRegisterSignificantEvent:
    significant_event_code: int
    description: str
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cufd_event: str  # Valor del CUFD que se uso en la contingencia.
    cuis: str
    nit: int
    start_datetime_event: str
    end_datetime_event: str
    enviroment: int = SIAT_ENVIROMENTS.TEST


@dataclass
class ResponseRegisterSignificantEvent:
    raw_response: Any
    code_significant_event: int
    # list_point_of_sales: List[Any]


@feature(CommandRegisterSignificantEvent)
class RegisterSignificantEvent(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OPERACIONES

    def execute(
        self, param_object: CommandRegisterSignificantEvent
    ) -> ResponseRegisterSignificantEvent:
        response = self.client.service.registroEventoSignificativo(
            SolicitudEventoSignificativo={
                "codigoAmbiente": param_object.enviroment,
                "codigoMotivoEvento": param_object.significant_event_code,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cufd": param_object.cufd,
                "cufdEvento": param_object.cufd_event,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
                "fechaHoraFinEvento": datetime_for_send_invoice(
                    param_object.end_datetime_event
                ),
                "fechaHoraInicioEvento": datetime_for_send_invoice(
                    param_object.start_datetime_event
                ),
                "descripcion": param_object.description,
            }
        )

        return ResponseRegisterSignificantEvent(
            raw_response=response,
            code_significant_event=response["codigoRecepcionEventoSignificativo"],
        )
