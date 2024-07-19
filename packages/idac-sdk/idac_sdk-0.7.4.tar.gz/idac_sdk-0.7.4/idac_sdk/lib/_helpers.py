from base64 import b64encode
from functools import cache
import hashlib
import secrets
from time import time
import json


def get_worker_hash(client_id: str, secret: str) -> str:
    timestamp = time.time()
    nonce = secrets.token_urlsafe()
    token_payload = {
        'client_id': client_id,
        'timestamp': timestamp,
        'access_token': hash_token(f"{secret}.{timestamp}.{nonce}"),
        'nonce': nonce
    }
    return json.dumps(token_payload)


@cache
def hash_token(payload: str) -> str:
    hasher = hashlib.sha3_256()
    hasher.update(payload.encode())
    digest = b64encode(hasher.digest()).decode()
    return digest
