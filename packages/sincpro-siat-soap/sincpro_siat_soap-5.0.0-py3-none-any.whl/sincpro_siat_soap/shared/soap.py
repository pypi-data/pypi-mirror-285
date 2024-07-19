from functools import lru_cache
from typing import Dict, Literal, Optional, TypeVar

from requests import Session
from zeep import Client
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport

from .global_definitions import (
    SIAT_ENVIROMENTS,
    SIAT_MODALITY,
    SIAT_PRODUCTION_ENDPOINTS,
    SIAT_TESTING_ENDPOINTS,
    use_facturacion_computarizada_enpoints,
    use_facturacion_electronica_enpoints,
)
from .logger import logger
from .utils import timeout_with_check_exists_response

WSDL_URL = TypeVar("WSDL_URL", str, None)


def build_token_header(token):
    header = {"apikey": f"TokenApi {token}"}
    return header


@timeout_with_check_exists_response(10)
def factory_soap_client(
    wsdl: str, headers: dict = None, cache_file_name: str = None
) -> Client:
    cache = None
    if cache_file_name is not None:
        cache_db_fs_path = f"/tmp/{cache_file_name}.db"
        logger.debug(f"Building CACHE ---> {cache_db_fs_path}")
        cache_ttl = 3600 * 8
        cache = SqliteCache(path=cache_db_fs_path, timeout=cache_ttl)

    transport = Transport(timeout=15, cache=cache, operation_timeout=23)

    if headers:
        session = Session()
        session.headers.update(headers)
        transport.session = session

    return Client(wsdl=wsdl, transport=transport)


def factory_services(map_of_endpoints: dict, token: str = None) -> Dict[str, Client]:
    header = None
    if token:
        header = build_token_header(token)

    services_dict = dict()

    for service_name, wsdl in map_of_endpoints.items():
        logger.info(f"Generating: [{service_name}]")
        logger.debug(f"-> {wsdl}")
        try:
            soap_client = factory_soap_client(
                wsdl, headers=header, cache_file_name=service_name
            )
        except Exception as error:
            logger.error(f"Error creating the soap client for {service_name}")
            logger.error(error, exc_info=True)
            soap_client = None
        services_dict[service_name] = soap_client
    return services_dict


def build_siat_endpoint_map(
    siat_environment: Literal[1, 2], modality: int = None
) -> Dict[str, WSDL_URL]:
    if isinstance(siat_environment, str):
        siat_environment = int(siat_environment)
    if isinstance(modality, str):
        modality = int(modality)
    logger.info(f"SIAT Environment: {siat_environment}, modality: {modality}")

    switch_case = {
        SIAT_ENVIROMENTS.TEST: SIAT_TESTING_ENDPOINTS,
        SIAT_ENVIROMENTS.PRODUCTION: SIAT_PRODUCTION_ENDPOINTS,
    }

    endpoint_hash_map = switch_case[siat_environment]

    if modality:
        if modality == SIAT_MODALITY.ELECTRONICA:
            endpoint_hash_map = use_facturacion_electronica_enpoints(
                endpoint_hash_map, siat_environment
            )
        if modality == SIAT_MODALITY.COMPUTARIZADA:
            endpoint_hash_map = use_facturacion_computarizada_enpoints(
                endpoint_hash_map, siat_environment
            )
        logger.debug(f"With Injected ENDPOINTS: \n{endpoint_hash_map}")
    return endpoint_hash_map


# Error: now is commented due this one was bringing inconsistency this module work as memoize based on incoming
# params
# @lru_cache()
def get_siat_soap_clients_map(
    siat_environment: Literal[1, 2], token: str = None, modality: int = None
) -> dict:
    if isinstance(siat_environment, str):
        siat_environment = int(siat_environment)
    if isinstance(modality, str):
        modality = int(modality)

    siat_endpoint_map = build_siat_endpoint_map(siat_environment, modality)
    return factory_services(siat_endpoint_map, token)


class ProxySiatServices:
    def __init__(
        self, siat_environment: Literal[1, 2] = 2, token: str = None, modality: int = None
    ):
        self.siat_environment = siat_environment
        self.token = token
        self.modality = modality
        self.siat_services: Optional[Dict[str, Client]] = None
        self.setup()

    def setup(self):
        self.siat_services = get_siat_soap_clients_map(
            self.siat_environment, self.token, self.modality
        )
        return self.siat_services

    def regenerate_all_soap_clients_that_are_none(self):
        for service_name in self.siat_services.keys():
            if self.siat_services[service_name] is None:
                siat_endpoints_map = build_siat_endpoint_map(
                    self.siat_environment, self.modality
                )

                try:
                    self.siat_services[service_name] = factory_soap_client(
                        siat_endpoints_map[service_name],
                        headers=build_token_header(self.token),
                        cache_file_name=service_name,
                    )

                except Exception as error:
                    logger.error(f"Error re-creating the soap client for {service_name}")
                    logger.error(error, exc_info=True)
                    self.siat_services[service_name] = None
