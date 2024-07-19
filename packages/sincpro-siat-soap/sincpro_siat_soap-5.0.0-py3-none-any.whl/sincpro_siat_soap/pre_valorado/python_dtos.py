from dataclasses import dataclass
from typing import List, Union


@dataclass(kw_only=True)
class PreValoradoDTO:
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
    codigoCliente: str
    codigoMetodoPago: int
    numeroTarjeta: Union[int, None]
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int
    montoTotalMoneda: float
    leyenda: str
    usuario: str
    codigoDocumentoSector: int


@dataclass(kw_only=True)
class PreValoradoDetailDTO:
    actividadEconomica: str
    codigoProductoSin: int
    codigoProducto: str
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


@dataclass()
class PreValoradoInvoiceDTO:
    header: Union[dict, PreValoradoDTO]
    details: List[Union[dict, PreValoradoDetailDTO]]
