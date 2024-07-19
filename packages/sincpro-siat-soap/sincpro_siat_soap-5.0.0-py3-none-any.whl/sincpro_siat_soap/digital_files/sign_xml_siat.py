import re
from dataclasses import dataclass, field

from sincpro_siat_soap.registry import feature
from sincpro_siat_soap.shared.UseCase import UseCase

from .infrastructure.xml_helper.xml_functions import sign_xml_root, xml_to_canonical_c14n


@dataclass
class CommandSignXML:
    xml: str
    key: str = field(repr=False)
    cert: str = field(repr=False)


@dataclass
class ResponseSignXML:
    xml: str


@feature(CommandSignXML)
class SignXMLSiat(UseCase):
    def execute(self, param_object: CommandSignXML) -> ResponseSignXML:
        signed_xml = sign_xml_root(param_object.xml, param_object.key, param_object.cert)
        # validate_signed_xml(param_object.cert, signed_xml)
        string_xml = xml_to_canonical_c14n(signed_xml)
        return ResponseSignXML(xml=string_xml.decode("utf-8"))
