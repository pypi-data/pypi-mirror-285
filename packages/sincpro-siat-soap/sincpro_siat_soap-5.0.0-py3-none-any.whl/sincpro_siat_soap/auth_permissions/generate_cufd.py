from dataclasses import dataclass

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_WSDL,
)
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandGenerateCUFD:
    nit: int
    system_code: str
    point_of_sale: int
    branch_office: int
    cuis: str
    environment: int = SIAT_ENVIROMENTS.TEST
    billing_type: int = SIAT_MODALITY.ELECTRONICA
    token = None


@dataclass()
class ResponseGenerateCUFD:
    cufd: str
    control_code: str
    raw_response: str


@feature(CommandGenerateCUFD)
class GenerateCUFD(UseCase):
    def wsdl(self) -> str:
        return SIAT_WSDL.OBTENCION_CODIGO

    def execute(self, param_object: CommandGenerateCUFD) -> ResponseGenerateCUFD:
        response = self.client.service.cufd(
            SolicitudCufd={
                "codigoAmbiente": param_object.environment,
                "codigoModalidad": param_object.billing_type,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "codigoPuntoVenta": param_object.point_of_sale,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        if response["codigo"] is None or response["codigoControl"] is None:
            raise Exception(f"Error: the cufd was not able to be generated:\n{response}")

        return ResponseGenerateCUFD(
            raw_response=response,
            cufd=response["codigo"],
            control_code=response["codigoControl"],
        )
