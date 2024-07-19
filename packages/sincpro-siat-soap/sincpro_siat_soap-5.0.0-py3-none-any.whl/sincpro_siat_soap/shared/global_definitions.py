import re


class SIAT_FIELD_WIDTH:
    NIT: int = 13
    DATETIME: int = 17
    BRANCH_OFFICE: int = 4
    DOCUMENT_TYPE: int = 2
    INVOICE_NUMBER: int = 10
    POINT_OF_SALE: int = 4


class SIAT_ENVIROMENTS:
    PRODUCTION: int = 1
    TEST: int = 2


class SIAT_MODALITY:
    ELECTRONICA: int = 1
    COMPUTARIZADA: int = 2


# ----------------------------------------------------------------------------------------------------------------------
# Version: 3.0 -> TODO: This one should be dynamically from a external
# ----------------------------------------------------------------------------------------------------------------------
class SIAT_WSDL:
    OBTENCION_CODIGO = "OBTERCION_CODIGO"
    SINCRONIZACION_DE_DATOS = "SINCRONIZACION_DE_DATOS"
    OPERACIONES = "OPERACIONES"
    COMPRAS = "COMPRAS"
    NOTA_DE_CREDITO = "NOTA_DE_CREDITO"
    FACTURA_COMPRA_VENTA = "FACTURA_COMPRA_VENTA"
    FACTURA_COMERCIAL_DE_EXPORTACION = "FACTURA_COMERCIAL_DE_EXPORTACION"
    FACTURA_SECTOR_EDUCATIVO = "FACTURA_SECTOR_EDUCATIVO"
    FACTURA_SECTOR_HOTEL = "FACTURA_SECTOR_HOTEL"
    FACTURA_PREVALORADO = "FACTURA_PREVALORADO"
    FACTURA_PREVALORADO_SDCF = "FACTURA_PREVALORADO_SIN_DERECHO_A_CREDITO_FISCAL"
    FACTURA_ALQUILER_DE_BIENES = "FACTURA_ALQUILER_DE_BIENES"
    SERVICIOS_ELECTRONICA = "SERVICIOS_ELECTRONICA"
    SERVICIOS_COMPUTARIZADA = "SERVICIOS_COMPUTARIZADA"


REGEX_PRIVATE_ATTR = re.compile("^__.*")
LIST_OF_CONSTANTS = lambda def_class: list(
    filter(lambda key: not REGEX_PRIVATE_ATTR.match(key), def_class.__dict__.keys())
)

LIST_OF_SERVICES = LIST_OF_CONSTANTS(SIAT_WSDL)

# ----------------------------------------------------------------------------------------------------------------------
# Shared Endpoints for ELECTRINICA and COMPUTARIZADA
# ----------------------------------------------------------------------------------------------------------------------

SIAT_TESTING_ENDPOINTS = {
    SIAT_WSDL.OBTENCION_CODIGO: "https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionCodigos?wsdl",
    SIAT_WSDL.SINCRONIZACION_DE_DATOS: "https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl",
    SIAT_WSDL.OPERACIONES: "https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl",
    SIAT_WSDL.COMPRAS: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioRecepcionCompras?wsdl",
    SIAT_WSDL.NOTA_DE_CREDITO: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionDocumentoAjuste?wsdl",
    SIAT_WSDL.FACTURA_COMPRA_VENTA: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionCompraVenta?wsdl",
}

SIAT_PRODUCTION_ENDPOINTS = {
    SIAT_WSDL.OBTENCION_CODIGO: "https://siatrest.impuestos.gob.bo/v2/FacturacionCodigos?wsdl",
    SIAT_WSDL.SINCRONIZACION_DE_DATOS: "https://siatrest.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl",
    SIAT_WSDL.OPERACIONES: "https://siatrest.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl",
    SIAT_WSDL.COMPRAS: "https://siatrest.impuestos.gob.bo/v2/ServicioRecepcionCompras?wsdl",
    SIAT_WSDL.NOTA_DE_CREDITO: "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionDocumentoAjuste?wsdl",
    SIAT_WSDL.FACTURA_COMPRA_VENTA: "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionCompraVenta?wsdl",
}

TEST_ELECTRONICA_COMMON_URL = (
    "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionElectronica?wsdl"
)
PROD_ELECTRONICA_COMMON_URL = (
    "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionElectronica?wsdl"
)

TEST_COMPUTARIZADA_COMMON_URL = (
    "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionComputarizada?wsdl"
)
PROD_COMPUTARIZADA_COMMON_URL = (
    "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionComputarizada?wsdl"
)

# ----------------------------------------------------------------------------------------------------------------------
# Endpoints by Modality
# ----------------------------------------------------------------------------------------------------------------------
SIAT_ELECTRONICA_ENDPOINTS = {
    SIAT_ENVIROMENTS.TEST: {
        SIAT_WSDL.SERVICIOS_ELECTRONICA: TEST_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_COMERCIAL_DE_EXPORTACION: TEST_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_EDUCATIVO: TEST_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_HOTEL: TEST_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO: TEST_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO_SDCF: TEST_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_ALQUILER_DE_BIENES: TEST_ELECTRONICA_COMMON_URL,
    },
    SIAT_ENVIROMENTS.PRODUCTION: {
        SIAT_WSDL.SERVICIOS_ELECTRONICA: PROD_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_COMERCIAL_DE_EXPORTACION: PROD_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_EDUCATIVO: PROD_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_HOTEL: PROD_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO: PROD_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO_SDCF: PROD_ELECTRONICA_COMMON_URL,
        SIAT_WSDL.FACTURA_ALQUILER_DE_BIENES: PROD_ELECTRONICA_COMMON_URL,
    },
}

SIAT_COMPUTARIZADA_ENDPOINTS = {
    SIAT_ENVIROMENTS.TEST: {
        SIAT_WSDL.SERVICIOS_COMPUTARIZADA: TEST_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_COMERCIAL_DE_EXPORTACION: TEST_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_EDUCATIVO: TEST_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_HOTEL: TEST_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO: TEST_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO_SDCF: TEST_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_ALQUILER_DE_BIENES: TEST_COMPUTARIZADA_COMMON_URL,
    },
    SIAT_ENVIROMENTS.PRODUCTION: {
        SIAT_WSDL.SERVICIOS_COMPUTARIZADA: PROD_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_COMERCIAL_DE_EXPORTACION: PROD_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_EDUCATIVO: PROD_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_SECTOR_HOTEL: PROD_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO: PROD_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_PREVALORADO_SDCF: PROD_COMPUTARIZADA_COMMON_URL,
        SIAT_WSDL.FACTURA_ALQUILER_DE_BIENES: PROD_COMPUTARIZADA_COMMON_URL,
    },
}

# ----------------------------------------------------------------------------------------------------------------------
# Util Functions to inject endpoints based on modality (ELECTRONICA or COMPUTARIZADA)
# ----------------------------------------------------------------------------------------------------------------------
use_facturacion_electronica_enpoints = lambda endpoints, environment: {
    **endpoints,
    **SIAT_ELECTRONICA_ENDPOINTS[environment],
}

use_facturacion_computarizada_enpoints = lambda endpoints, environment: {
    **endpoints,
    **SIAT_COMPUTARIZADA_ENDPOINTS[environment],
}
