from dataclasses import dataclass
from typing import Dict, List, Literal, Union

from sincpro_siat_soap.digital_files.infrastructure.xml_helper.siat_template import (
    SIAT_XML_Template,
)
from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.UseCase import UseCase

education_document = Literal[
    "facturaElectronicaHotel",
    "facturaComputarizadaHotel",
]


@dataclass
class CommandGenerate_SIAT_XML_SectorHotel:
    cabecera: Dict
    detalle: List[Dict]
    node_name: Union[education_document, str] = "facturaElectronicaHotel"


@dataclass
class ResponseGenerate_SIAT_XML_SectorHotel:
    xml: str
    root_element: any


@feature(CommandGenerate_SIAT_XML_SectorHotel)
class Generate_SIAT_XML_SectorHotel(UseCase):
    def execute(
        self, param_object: CommandGenerate_SIAT_XML_SectorHotel
    ) -> ResponseGenerate_SIAT_XML_SectorHotel:
        template = SIAT_XML_Template(param_object.node_name)
        template.add_header(param_object.cabecera)
        template.add_details(param_object.detalle)
        template.build_xml_obj()
        xml = template.generate_string_xml()
        return ResponseGenerate_SIAT_XML_SectorHotel(
            xml=xml, root_element=template.python_root_obj()
        )
