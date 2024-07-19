from typing import Any, Dict, Union

from zeep import Client

from sincpro_siat_soap.shared.global_definitions import SIAT_WSDL


# ----------------------------------------------------------------------------------------------------------------------
# Main Abstraction for application layer
# This one Represent the features of all the library
# -----------------------------------------------------------------------------------------------------------------------
class UseCase:
    def __init__(self, siat_services: Dict[str, Client]):
        self.client = siat_services.get(self.wsdl(), None)

    def wsdl(self) -> str:
        """
        Override in the children (Template method pattern)
        :return: url of WSDL
        """
        return SIAT_WSDL.OBTENCION_CODIGO

    def execute(self, param_object) -> Union[Any, None]:
        pass
