import struct
from base64 import b64encode
from hashlib import sha256
from typing import Union

from sincpro_siat_soap.shared.logger import logger

# from cryptography.hazmat.primitives import serialization, hashes, _serialization
# from cryptography.hazmat.primitives.asymmetric import types
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.backends import default_backend
# from cryptography import x509


def long_to_bytes(n, blocksize=0):
    """long_to_bytes(n:long, blocksize:int) : string
    Convert a long integer to a byte string.

    If optional blocksize is given and greater than zero, pad the front of the
    byte string with binary zeros so that the length is a multiple of
    blocksize.
    """
    # after much testing, this algorithm was deemed to be the fastest
    s = b""

    pack = struct.pack
    while n > 0:
        s = pack(b">I", n & 0xFFFFFFFF) + s
        n = n >> 32
    # strip off leading zeros
    for i in range(len(s)):
        if s[i] != b"\000"[0]:
            break
    else:
        # only happens when n == 0
        s = b"\000"
        i = 0
    s = s[i:]
    # add back some pad bytes.  this could be done more efficiently w.r.t. the
    # de-padding being done above, but sigh...
    if blocksize > 0 and len(s) % blocksize:
        s = (blocksize - len(s) % blocksize) * b"\000" + s
    return s


def get_hash_base64(data: Union[bytes, str], in_string_format=True) -> Union[bytes, str]:
    data_to_transform = data

    if isinstance(data, str):
        data_to_transform = data.encode("utf-8")

    hash = sha256(data_to_transform)
    hash_base64 = b64encode(hash.digest())

    if in_string_format is True:
        return hash_base64.decode("utf-8")

    return hash_base64


# def serialize_private_key(private_key: Union[bytes, str]) -> types.rsa.RSAPrivateKey:
#     logger.info('Serializing the private key')
#     binary_private_key = private_key

#     if isinstance(binary_private_key, str):
#         binary_private_key = private_key.encode('utf-8')

#     return serialization.load_pem_private_key(
#         binary_private_key,
#         password=None,
#         backend=default_backend()
#     )


# def priv_key_rsa_sign(serialized_private_key: types.rsa.RSAPrivateKey, message: Union[bytes, str]) -> bytes:
#     logger.info(f'Private key encrypting the message: [{message}]')
#     message_to_encrypt = message

#     if isinstance(message, str):
#         message_to_encrypt = message_to_encrypt.encode('utf-8')

#     return serialized_private_key.sign(
#         data=message_to_encrypt,
#         padding=padding.PKCS1v15(),
#         algorithm=hashes.SHA256()
#     )


# def generate_public_key_from_cert(cert: Union[str, bytes], in_string_format=True) -> Union[str, bytes]:
#     logger.info(f'Generating a public key from \n {cert}')
#     _cert = cert
#     if isinstance(cert, str):
#         _cert = cert.encode('utf-8')

#     serialized_cert = x509.load_pem_x509_certificate(_cert)
#     public_key = serialized_cert.public_key()

#     formated_public_key = public_key.public_bytes(
#         encoding=_serialization.Encoding.OpenSSH,
#         format=_serialization.PublicFormat.OpenSSH
#     )
#     logger.info(f'Public key: \n {formated_public_key.decode("utf-8")}')

#     if in_string_format is True:
#         return formated_public_key.decode('utf-8')

#     return formated_public_key


# def remove_header_and_footer_from_cert(key_string: str) -> str:
#     string_array = key_string.splitlines()
#     removed_header_fotter = string_array[1:len(string_array) - 1]
#     return '\n'.join(removed_header_fotter)
#     # header_to_remove = '-----BEGIN PUBLIC KEY-----'
#     # footer_to_remove = '-----END PUBLIC KEY-----'
