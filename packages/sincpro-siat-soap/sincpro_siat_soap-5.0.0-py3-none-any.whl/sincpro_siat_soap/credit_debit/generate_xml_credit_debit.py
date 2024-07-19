from dataclasses import dataclass
from typing import Dict, List

from sincpro_siat_soap.digital_files.infrastructure.xml_helper.siat_template import (
    SIAT_XML_Template,
)
from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.UseCase import UseCase


@dataclass
class CommandGenerateCreditDebitXML:
    cabecera: Dict
    detalles: List[Dict]
    node_name: str = "notaFiscalElectronicaCreditoDebito"


@dataclass
class ResponseGenerateCreditDebitXML:
    xml: str
    root_element: any


@feature(CommandGenerateCreditDebitXML)
class GenerateCreditDebitXML(UseCase):
    def execute(
        self, param_object: CommandGenerateCreditDebitXML
    ) -> ResponseGenerateCreditDebitXML:
        template = SIAT_XML_Template(param_object.node_name)
        template.add_header(param_object.cabecera)
        template.add_details(param_object.detalles)

        template.build_xml_obj()
        xml = template.generate_string_xml()

        return ResponseGenerateCreditDebitXML(
            xml=xml, root_element=template.python_root_obj()
        )
