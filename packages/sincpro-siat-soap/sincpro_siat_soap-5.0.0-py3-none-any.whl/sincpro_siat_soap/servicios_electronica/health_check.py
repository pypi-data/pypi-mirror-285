from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandCheckHealthElectronica:
    pass


@dataclass
class ResponseCheckHealthElectronica:
    is_up: bool


@feature(CommandCheckHealthElectronica)
class CheckHealth(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.SERVICIOS_ELECTRONICA

    def execute(
        self, param_object: CommandCheckHealthElectronica
    ) -> ResponseCheckHealthElectronica:
        response = self.client.service.verificarComunicacion()
        return ResponseCheckHealthElectronica(response["transaccion"])
