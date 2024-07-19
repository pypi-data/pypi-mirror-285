from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class HospitalSectorHeaderDTO:
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
    modalidadServicio: str
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
class HospitalSectorDetailDTO:
    actividadEconomica: str
    codigoProductoSin: int
    codigoProducto: str
    descripcion: str
    especialidad: Optional[str]  # Hospital -  Producto
    especialidadDetalle: Optional[str]  # Hospital  - Producto
    nroQuirofanoSalaOperaciones: int  # Hospital -  Producto
    especialidadMedico: Optional[str]  # Hospital - Medico Informacion
    nombreApellidoMedico: str  # Hospital - Medico Informacion
    nitDocumentoMedico: str  # Hospital  - Medico Informacion
    nroMatriculaMedico: Optional[str]  # Hospital  - Medico Informacion
    nroFacturaMedico: Optional[str]  # Hospital  - Medico Factura
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


@dataclass
class EducationSectorDTO:
    header: Union[Dict, HospitalSectorHeaderDTO]
    details: Union[List[Dict], List[HospitalSectorDetailDTO]]
