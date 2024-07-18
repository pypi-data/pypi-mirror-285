import os
from solders.keypair import Keypair
from abstract_security import get_env_value
import base58
import sys
import json
def load_from_private_key(env_key='AMM_P'):
    env_value = get_env_value(key=env_key)
    if env_value:
        return Keypair.from_base58_string(env_value)

def load_keypair_from_file(filename):
    curr = os.path.join(sys.path[0], 'data',  filename)
    with open(curr, 'r') as file:
        secret = json.load(file)
        secret_key = bytes(secret)
        # print(base58.b58encode(secret_key))
        return Keypair.from_bytes(secret_key)
