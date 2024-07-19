from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandCheckHealth:
    pass


@dataclass
class ResponseCheckHealth:
    is_up: bool


@feature(CommandCheckHealth)
class CheckHealth(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.FACTURA_COMPRA_VENTA

    def execute(self, param_object: CommandCheckHealth) -> ResponseCheckHealth:
        response = self.client.service.verificarComunicacion()
        return ResponseCheckHealth(response["transaccion"])
