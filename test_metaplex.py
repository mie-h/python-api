import os
import base58
from solana.rpc.api import Client
from api.metaplex_api import MetaplexAPI
from cryptography.fernet import Fernet

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
cfg = {
    "PRIVATE_KEY": base58.b58encode(PRIVATE_KEY).decode("ascii"),
    "PUBLIC_KEY": str(PUBLIC_KEY),
    "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
}
api_endpoint = "https://api.devnet.solana.com/"
Client(api_endpoint).request_airdrop(PUBLIC_KEY, int(1e10))
print("done airdrop")

# Create API
metaplex_api = MetaplexAPI(cfg)
print("crated API")

# Deploy
metaplex_api.deploy(api_endpoint, "A" * 32, "A" * 10, 0)
print("deployed")
