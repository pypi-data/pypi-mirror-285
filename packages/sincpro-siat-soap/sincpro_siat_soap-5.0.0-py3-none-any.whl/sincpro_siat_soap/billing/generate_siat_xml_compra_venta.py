from dataclasses import dataclass
from typing import Dict, List

from sincpro_siat_soap.digital_files.infrastructure.xml_helper.siat_template import (
    SIAT_XML_Template,
)
from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandGenerate_SIAT_XML_CompraVenta:
    cabecera: Dict
    detalle: List[Dict]
    node_name: str = "facturaElectronicaCompraVenta"


@dataclass
class ResponseGenerate_SIAT_XML_CompraVenta:
    xml: str
    root_element: any


@feature(CommandGenerate_SIAT_XML_CompraVenta)
class Generate_SIAT_XML_CompraVenta(UseCase):
    def execute(
        self, param_object: CommandGenerate_SIAT_XML_CompraVenta
    ) -> ResponseGenerate_SIAT_XML_CompraVenta:
        template = SIAT_XML_Template(param_object.node_name)
        template.add_header(param_object.cabecera)
        template.add_details(param_object.detalle)

        template.build_xml_obj()
        xml = template.generate_string_xml()

        return ResponseGenerate_SIAT_XML_CompraVenta(
            xml=xml, root_element=template.python_root_obj()
        )
