from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class DebitCreditHeaderDTO:
    nitEmisor: int
    razonSocialEmisor: str
    municipio: str
    telefono: str
    numeroNotaCreditoDebito: int
    cuf: str
    cufd: str
    codigoSucursal: int
    direccion: str
    codigoPuntoVenta: int
    fechaEmision: str
    nombreRazonSocial: str
    codigoTipoDocumentoIdentidad: int
    numeroDocumento: int
    complemento: str
    codigoCliente: Union[str, int]
    numeroFactura: int
    numeroAutorizacionCuf: str
    fechaEmisionFactura: str
    montoTotalOriginal: float
    montoTotalDevuelto: float
    montoDescuentoCreditoDebito: float
    montoEfectivoCreditoDebito: float
    codigoExcepcion: str
    leyenda: str
    usuario: Union[str, int]
    codigoDocumentoSector: int


@dataclass
class DebitCreditDetailDTO:
    actividadEconomica: Union[str, int]
    codigoProductoSin: Union[str, int]
    codigoProducto: Union[str, int]
    descripcion: str
    cantidad: Union[float, int]
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float
    codigoDetalleTransaccion: str


@dataclass
class DebitCreditDTO:
    header: Union[Dict, DebitCreditHeaderDTO]
    details: Union[List[Dict], List[DebitCreditDetailDTO]]
