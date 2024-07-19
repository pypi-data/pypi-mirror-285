from typing import Callable, Dict, List, Union

from sincpro_siat_soap.shared.core_exceptions import SIATException
from sincpro_siat_soap.shared.logger import logger


def generate_message_based_on_list(message_list: List[Dict]) -> Union[str, None]:
    error_message = ""
    if message_list is None:
        return None

    if isinstance(message_list, list):
        for index, message in enumerate(message_list):
            codigo = message["codigo"]
            description = message["descripcion"]
            error_message = (
                f"{error_message} \n {index + 1}: Codigo [{codigo}] - {description}"
            )

    return error_message


def siat_exception_builder(raw_response: Dict) -> Callable[[], SIATException]:
    code = raw_response["codigoEstado"]
    state = raw_response["codigoEstado"]

    message = "Error"
    logger.error(f"{raw_response}")
    if code and state:
        if raw_response["mensajesList"]:
            error_message = generate_message_based_on_list(raw_response["mensajesList"])
            if error_message:
                message = f"{message}\n {error_message}"

    def call_error_fn():
        raise SIATException(message)

    return call_error_fn
