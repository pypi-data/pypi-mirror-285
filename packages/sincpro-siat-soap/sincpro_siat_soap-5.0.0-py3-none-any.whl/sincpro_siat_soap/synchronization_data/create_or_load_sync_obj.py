import os
import pickle
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Tuple, Union

import pytz

from sincpro_siat_soap import use_case
from sincpro_siat_soap.auth_permissions import CommandGenerateCUFD, ResponseGenerateCUFD
from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_ENVIROMENTS, SIAT_MODALITY
from sincpro_siat_soap.shared.logger import logger
from sincpro_siat_soap.shared.UseCase import UseCase
from sincpro_siat_soap.shared.utils import SincproTimeoutException, timeout


@dataclass
class HitoricalCUFD:
    control_code: str
    cufd: str
    address: str
    raw_cufd: Any


class SynchronizationObject:
    def __init__(
        self,
        nit,
        cuis,
        branch_office,
        system_code,
        point_of_sale,
        obj_binary_dir="/opt/siat/",
        modality=SIAT_MODALITY.ELECTRONICA,
        environment=SIAT_ENVIROMENTS.TEST,
    ):
        self.nit: Union[int, str] = nit
        self.cuis: str = cuis
        self.branch_office: int = branch_office
        self.system_code: str = system_code
        self.point_of_sale: int = point_of_sale

        self.cufd_date: Union[date, None] = None
        self.cufd_response: Union[ResponseGenerateCUFD, None] = None
        self.cufd: Union[str, None] = None
        self.control_code: Union[str, None] = None
        self.address: Union[str, None] = None

        self.historical_cufd: Dict[Tuple[datetime, datetime], HitoricalCUFD] = dict()

        self.current_date: datetime = datetime.now()
        self.obj_binary_dir: str = obj_binary_dir
        self.modality: int = modality
        self.environment: int = environment

        self.commands = []

    def sync(self):
        self.current_date: datetime = datetime.now()
        self.build_object_binary()

    def build_object_binary(self):
        file_name = f"{self.__class__.__name__}{self.point_of_sale}{self.branch_office}"
        logger.debug(
            f"Building/Serializing the SYNC OBJ in the path: [{self.obj_binary_dir}{file_name}]"
        )
        binary = pickle.dumps(self)
        with open(f"{self.obj_binary_dir}{file_name}", "wb") as file:
            file.write(binary)

    def request_new_cufd(self):
        # TODO: add timeout and if there is 3 attemps return the old
        logger.info(f"Replacing old CUFD and generating a new one: {self.obj_binary_dir}")
        self._store_old_cufd()
        command = CommandGenerateCUFD(
            nit=self.nit,
            system_code=self.system_code,
            point_of_sale=self.point_of_sale,
            branch_office=self.branch_office,
            cuis=self.cuis,
            environment=self.environment,
            billing_type=self.modality,
        )

        self.cufd_response = use_case.execute(command)
        self.cufd_date = datetime.today().date()
        self.cufd = self.cufd_response.cufd
        self.control_code = self.cufd_response.control_code
        self.address = self.cufd_response.raw_response["direccion"]
        self.current_date = datetime.now()
        self.build_object_binary()
        return self.cufd_response

    def force_sync(self):
        logger.info(f"Force sync process")
        self.sync()

    def __str__(self):
        string_information = f"""
            point_of_sale: {self.point_of_sale}
            system_code: {self.system_code}
            nit: {self.nit}
            cuis: {self.cuis}
            branch_office: {self.branch_office}
            cufd: {self.cufd_response.cufd}    
            modality: {self.modality}
            environment: {self.environment}
        """
        return string_information

    def __repr__(self):
        return f"""
            point_of_sale: {self.point_of_sale}
            system_code: {self.system_code}
            nit: {self.nit}
            cuis: {self.cuis}
            branch_office: {self.branch_office}
            cufd: {self.cufd_response.cufd}    
            modality: {self.modality}
            environment: {self.environment}
        """

    @staticmethod
    def obj(
        binary_dir: str = "/opt/sincpro/storage",
        point_of_sale: int = 0,
        branch_office: int = 0,
    ) -> "SynchronizationObject":
        file_name = (
            f"{binary_dir}{SynchronizationObject.__name__}{point_of_sale}{branch_office}"
        )
        logger.debug(f"Loading sync obj from {file_name}")
        with open(f"{file_name}", "rb") as file:
            binary = file.read()
            logger.debug(f"Sync object Size: [{sys.getsizeof(binary)}]")
            sync_obj: SynchronizationObject = pickle.loads(binary)

            # TODO: add timeout and if there is 3 attemps return the old
            if (sync_obj.current_date + timedelta(hours=24)) < datetime.now():
                logger.info(
                    "Sync object out of date. building new sync obj and returning a new one "
                )
                sync_obj.request_new_cufd()
                sync_obj.sync()
                logger.debug(str(sync_obj))
                return sync_obj

            logger.debug("Returning current sync object")
            return sync_obj

    @staticmethod
    def old_obj(
        binary_dir: str = "/opt/sincpro/storage",
        point_of_sale: int = 0,
        branch_office: int = 0,
    ) -> "SynchronizationObject":
        file_name = (
            f"{binary_dir}{SynchronizationObject.__name__}{point_of_sale}{branch_office}"
        )
        logger.debug(f"Loading old sync obj from {file_name}")
        with open(f"{file_name}", "rb") as file:
            binary = file.read()
            logger.debug(f"Sync object Size: [{sys.getsizeof(binary)}]")
            sync_obj: SynchronizationObject = pickle.loads(binary)
        logger.debug("Returning current UNUPDATED Sync obj")
        return sync_obj

    def _store_old_cufd(self):
        logger.debug("Add CUFD to historical CUFDs")
        if not hasattr(self, "historical_cufd"):
            logger.debug("Historical CUFD is not defined, creating a new one")
            self.historical_cufd = dict()
        try:
            ttl_cufd = self.cufd_response.raw_response["fechaVigencia"]
            start_datetime = ttl_cufd - timedelta(days=1)
            end_datetime = datetime.now(tz=pytz.timezone("America/La_paz"))
            identifies = (start_datetime, end_datetime)
            self.historical_cufd[identifies] = HitoricalCUFD(
                control_code=self.control_code,
                cufd=self.cufd,
                address=self.address,
                raw_cufd=self.cufd_response,
            )
            if len(self.historical_cufd.keys()) > 30:
                list_keys = list(self.historical_cufd.keys())
                logger.debug(f"Removve the CUFD in dates {list_keys[0]}")
                del self.historical_cufd[list_keys[0]]

        except Exception as error:
            logger.error(
                f"The CUFD was not stored in the historical CUFDs: {self.cufd}", exc_info=True
            )


@dataclass
class CommandCreateOrLoadSyncObj:
    nit: int
    cuis: str
    branch_office: int
    point_of_sale: int
    system_code: str
    path_serialized: str
    environment: int = SIAT_ENVIROMENTS.TEST
    modality: int = SIAT_MODALITY.ELECTRONICA


@dataclass
class ResponseCreateOrLoadSyncObj:
    sync_obj: SynchronizationObject


@feature(CommandCreateOrLoadSyncObj)
class CreateOrLoadSyncObj(UseCase):
    def execute(
        self, param_object: CommandCreateOrLoadSyncObj
    ) -> ResponseCreateOrLoadSyncObj:
        try:
            timeout_value = os.getenv("SYNC_OBJ_TIMEOUT") or 10
            sync_obj_timeout_build_time = int(timeout_value)
            fn = timeout(sync_obj_timeout_build_time)
            return ResponseCreateOrLoadSyncObj(
                fn(SynchronizationObject.obj)(
                    param_object.path_serialized,
                    param_object.point_of_sale,
                    param_object.branch_office,
                )
            )

        except SincproTimeoutException as error:
            logger.error(
                "Timeout to rebuild the sync obj, returning the old one", exc_info=True
            )
            return ResponseCreateOrLoadSyncObj(
                SynchronizationObject.old_obj(
                    param_object.path_serialized,
                    param_object.point_of_sale,
                    param_object.branch_office,
                )
            )

        except FileNotFoundError as error:
            logger.error("Generating or creating a new sync object")
            sync_obj = SynchronizationObject(
                nit=param_object.nit,
                cuis=param_object.cuis,
                branch_office=param_object.branch_office,
                system_code=param_object.system_code,
                point_of_sale=param_object.point_of_sale,
                obj_binary_dir=param_object.path_serialized,
                environment=param_object.environment,
                modality=param_object.modality,
            )
            sync_obj.request_new_cufd()
            sync_obj.sync()
            logger.debug(str(sync_obj))
            return ResponseCreateOrLoadSyncObj(sync_obj)

        except Exception as error:
            logger.error("Error trying to build the sync obj", exc_info=True)
