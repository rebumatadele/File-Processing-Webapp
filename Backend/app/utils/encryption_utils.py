# app/utils/encryption_utils.py

import base64

def xor_bytes(data: bytes, key: bytes) -> bytes:
    if len(data) != len(key):
        raise ValueError("Data and key must be the same length to XOR.")
    return bytes(d ^ k for d, k in zip(data, key))

def base64_to_bytes(b64_str: str) -> bytes:
    return base64.b64decode(b64_str)

def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')
