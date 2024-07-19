from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class HotelInvoiceHeaderDTO:
    nitEmisor: int
    razonSocialEmisor: str
    municipio: str
    telefono: str
    numeroFactura: int
    cuf: str
    cufd: str
    codigoSucursal: int
    direccion: str
    codigoPuntoVenta: int
    fechaEmision: str
    nombreRazonSocial: str
    codigoTipoDocumentoIdentidad: int
    numeroDocumento: str
    complemento: str
    codigoCliente: str
    cantidadHuespedes: Union[int, None]
    cantidadHabitaciones: Union[int, None]
    cantidadMayores: Union[int, None]
    cantidadMenores: Union[int, None]
    fechaIngresoHospedaje: str
    codigoMetodoPago: int
    numeroTarjeta: Union[int, None]
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int
    montoTotalMoneda: float
    montoGiftCard: Union[bool, None]
    descuentoAdicional: Union[int, None]
    codigoExcepcion: str
    cafc: Union[str, None]
    leyenda: str
    usuario: str
    codigoDocumentoSector: int


@dataclass
class HotelInvoiceDetailDTO:
    actividadEconomica: str
    codigoProductoSin: int
    codigoProducto: str
    codigoTipoHabitacion: Union[int, None]
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float
    detalleHuespedes: Union[str, None]


@dataclass
class InvoiceDTO:
    header: Union[Dict, HotelInvoiceHeaderDTO]
    details: Union[List[Dict], List[HotelInvoiceDetailDTO]]
