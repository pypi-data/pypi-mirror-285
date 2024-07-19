# from dataclasses import dataclass
# from sincpro_siat_soap.shared.UseCase import UseCase
# from sincpro_siat_soap.registry import use_case

# from .infrastructure.xml_helper.xml_functions import (
#     xml_to_canonical_c14n,
#     build_signature_tags,
#     add_public_key_to_signature_node,
#     add_signature_value_to_signature_node,
#     add_signature_node_to_xml
# )

# from .infrastructure.helpers_encryption import (
#     get_hash_base64,
#     generate_public_key_from_cert,
#     serialize_private_key,
#     priv_key_rsa_sign,
#     remove_header_and_footer_from_cert,
#     b64encode,
#     sha256,
# )


# @dataclass
# class CommandSignXMLV2:
#     xml: str
#     key: str
#     cert: str


# @dataclass
# class ResponseSignXMLV2:
#     xml: str


# class SignXMLV2(UseCase):

#     def execute(self, param_object: CommandSignXMLV2) -> ResponseSignXMLV2:
#         invoice_parsed_to_canonical = xml_to_canonical_c14n(param_object.xml)
#         invoice_hash = get_hash_base64(invoice_parsed_to_canonical, in_string_format=True)

#         signature_node = build_signature_tags(invoice_hash)
#         signature_parsed_to_canonical = xml_to_canonical_c14n(signature_node)
#         signature_hash = sha256(signature_parsed_to_canonical).digest()

#         # Encryption process
#         private_key = serialize_private_key(param_object.key)
#         encrypted_message = priv_key_rsa_sign(private_key, signature_hash)  # Signature
#         encrypted_message_hash = b64encode(encrypted_message).decode('utf-8')

#         add_signature_value_to_signature_node(encrypted_message_hash, signature_node)

#         public_key = generate_public_key_from_cert(param_object.cert)
#         public_key_without_header_and_footer = remove_header_and_footer_from_cert(public_key)
#         add_public_key_to_signature_node(public_key_without_header_and_footer, signature_node)

#         xml_root_node = add_signature_node_to_xml(invoice_parsed_to_canonical, signature_node)

#         return ResponseSignXMLV2(xml_to_canonical_c14n(xml_root_node).decode('utf-8'))


# use_case.register(SignXMLV2(), CommandSignXMLV2)
