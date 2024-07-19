from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandCheckHealthComputarizada:
    pass


@dataclass
class ResponseCheckHealthComputarizada:
    is_up: bool


@feature(CommandCheckHealthComputarizada)
class CheckHealth(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SERVICIOS_COMPUTARIZADA

    def execute(
        self, param_object: CommandCheckHealthComputarizada
    ) -> ResponseCheckHealthComputarizada:
        response = self.client.service.verificarComunicacion()
        return ResponseCheckHealthComputarizada(response["transaccion"])
