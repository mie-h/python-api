import os
import base58
from api.metaplex_api import MetaplexAPI
from cryptography.fernet import Fernet


PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

cfg = {
    "PRIVATE_KEY": base58.b58encode(PRIVATE_KEY).decode("ascii"),
    "PUBLIC_KEY": str(PUBLIC_KEY),
    "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
}

# Create API
metaplex_api = MetaplexAPI(cfg)

response = metaplex_api.wallet()

print(f"response: {response}")
"""
{"address": "7hLeJJUYmp42WEhZamd1XwgoTFj2pyZe9RG685ogi9fb", "private_key": [11, 134, 4, 221, 103, 79, 18, 137, 162, 173, 251, 175, 19, 173, 45, 175, 144, 164, 122, 216, 126, 84, 90, 31, 157, 185, 74, 185, 157, 5, 7, 105]}
"""
