from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class EducationSectorHeaderDTO:
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
    nombreEstudiante: str
    periodoFacturado: str
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
class EducationSectorDetailDTO:
    actividadEconomica: str
    codigoProductoSin: int
    codigoProducto: str
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


@dataclass
class EducationSectorDTO:
    header: Union[Dict, EducationSectorHeaderDTO]
    details: Union[List[Dict], List[EducationSectorDetailDTO]]
