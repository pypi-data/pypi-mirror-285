from datetime import datetime
from typing import Union


def datetime_for_CUF(invoice_datetime: Union[str, datetime]) -> str:
    cuf_date_time_format = "%Y%m%d%H%M%S%f"

    if isinstance(invoice_datetime, datetime):
        return invoice_datetime.strftime(cuf_date_time_format)[:17]

    if isinstance(invoice_datetime, str):
        datetime_py_obj = datetime.fromisoformat(invoice_datetime)
        return datetime_py_obj.strftime(cuf_date_time_format)[:17]


def datetime_for_send_invoice(invoice_datetime: Union[str, datetime]) -> str:
    FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
    if isinstance(invoice_datetime, datetime):
        return invoice_datetime.strftime(FORMAT)[:23]

    if isinstance(invoice_datetime, str):
        datetime_py_obj = datetime.fromisoformat(invoice_datetime)
        return datetime_py_obj.strftime(FORMAT)[:23]
