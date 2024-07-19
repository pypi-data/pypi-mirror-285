from dataclasses import dataclass
from typing import Any

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandRevokeCerts:
    cert: str
    system_code: str
    branch_office: int
    cuis: str
    nit: int
    reason: str
    date_from_request_rovoke: str
    environment: int = SIAT_ENVIROMENTS.TEST
    billing_type: int = SIAT_MODALITY.ELECTRONICA


@dataclass
class ResponseRevokeCerts:
    was_revoked: str
    raw_reponse: Any


@feature(CommandRevokeCerts)
class RevokeCerts(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OBTENCION_CODIGO

    def execute(self, param_object: CommandRevokeCerts) -> ResponseRevokeCerts:
        response = self.client.service.notificaCertificadoRevocado(
            SolicitudNotificaRevocado={
                "certificado": param_object.cert,
                "codigoAmbiente": param_object.environment,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "fechaRevocacion": param_object.date_from_request_rovoke,
                "nit": param_object.nit,
                "razonRevocacion": param_object.reason,
            }
        )

        return ResponseRevokeCerts(was_revoked=response["transaccion"], raw_reponse=response)


# use_case.register(RevokeCerts(), CommandRevokeCerts)
