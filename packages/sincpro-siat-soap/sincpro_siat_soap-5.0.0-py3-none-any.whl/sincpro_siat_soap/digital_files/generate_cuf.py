from dataclasses import dataclass
from datetime import datetime
from typing import Union

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.global_definitions import SIAT_MODALITY
from sincpro_siat_soap.shared.UseCase import UseCase
from sincpro_siat_soap.shared.utils import (
    get_mod_eleven_digit,
    parse_integer_string_to_base16,
)

from .infrastructure.util_format import datetime_for_CUF


@dataclass
class CommandGenerateCUF:
    control_code: str
    nit: int
    date_time: Union[datetime, str]
    branch_office: int
    emission_type: int
    invoice_type: int
    type_sector_document: int
    invoice_num: int
    point_of_sale: int
    modality: int = SIAT_MODALITY.ELECTRONICA


@dataclass()
class ResponseGenerateCUF:
    cuf: str


@feature(CommandGenerateCUF)
class GenerateCUF(UseCase):
    # · NIT EMISOR = 0000123456789
    # · FECHA / HORA = 20190113163721231
    # · SUCURSAL = 0000
    # · MODALIDAD = 1 # ELECTORNICA, COMPUTARIZADA
    # · TIPO EMISIÓN = 1 # ONLINE, OFFLINE, ETC
    # · TIPO FACTURA / DOCUMENTO AJUSTE = 1
    # · TIPO DOCUMENTO SECTOR = 01
    # · NÚMERO DE FACTURA = 0000000001
    # · POS: 0000

    def execute(self, param_object: CommandGenerateCUF) -> ResponseGenerateCUF:
        invoice_date = datetime_for_CUF(param_object.date_time)
        code = (
            f"{str(param_object.nit).zfill(13)}"
            f"{invoice_date}"
            f"{str(param_object.branch_office).zfill(4)}"
            f"{param_object.modality}"
            f"{param_object.emission_type}"
            f"{param_object.invoice_type}"
            f"{str(param_object.type_sector_document).zfill(2)}"
            f"{str(param_object.invoice_num).zfill(10)}"
            f"{str(param_object.point_of_sale).zfill(4)}"
        )
        mod11_digit = get_mod_eleven_digit(code)
        code_plus_mod = code + mod11_digit
        cuf_code = (
            f"{parse_integer_string_to_base16(code_plus_mod)}{param_object.control_code}"
        )

        return ResponseGenerateCUF(cuf_code)
