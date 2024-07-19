import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from sincpro_siat_soap.registry import (
    container,
    factory_siat_services,
    factory_use_case,
    setup_dict,
)
from sincpro_siat_soap.shared.core_exceptions import SIATException
from sincpro_siat_soap.shared.global_definitions import SIAT_MODALITY
from sincpro_siat_soap.shared.logger import logger
from sincpro_siat_soap.shared.UseCaseExecutor import UseCaseError, UseCaseExecutor


# ----------------------------------------------------------------------------
# This one created a new use_case
# ----------------------------------------------------------------------------
def new_use_case() -> UseCaseExecutor:
    container.reset_singletons()
    return factory_use_case()


# ------------------------------------------------------------------------------------------------
# Interface, facade for the old version, this one work based on the env or setup_dict
# Basically this one can work as the old version
# ------------------------------------------------------------------------------------------------
class use_case:
    @staticmethod
    def execute(command: Any):
        use_case.check_injected_params()
        use_case.rebuild_siat_services_if_is_necessary()
        return factory_use_case().execute(command)

    @staticmethod
    def rebuild_siat_services_if_is_necessary():
        siat_proxy_services = factory_siat_services()
        if isinstance(siat_proxy_services.siat_services, dict):
            if None in siat_proxy_services.siat_services.values():
                siat_proxy_services.regenerate_all_soap_clients_that_are_none()

    @staticmethod
    def check_injected_params():
        if not container.injected_params().keys():
            siat_env = os.getenv("SIAT_ENVIRONMENT")
            siat_token = os.getenv("SIAT_TOKEN")

            siat_modality = os.getenv("SIAT_MODALITY", None)
            if siat_modality is None:
                siat_modality = SIAT_MODALITY.ELECTRONICA
            setup_dict(
                {
                    "siat_environment": siat_env,
                    "siat_token": siat_token,
                    "modality": siat_modality,
                }
            )
