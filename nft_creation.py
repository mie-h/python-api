import os
import json
import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey as PublicKey
from cryptography.fernet import Fernet
from api.metaplex_api import MetaplexAPI


PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
cfg = {
    "PRIVATE_KEY": base58.b58encode(PRIVATE_KEY).decode("ascii"),
    "PUBLIC_KEY": PUBLIC_KEY,
    "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
}
api_endpoint = "https://api.testnet.solana.com/"
# get SOL on account A
response = Client(api_endpoint).request_airdrop(
    PublicKey.from_string(PUBLIC_KEY), int(1e10)
)

print(f"response: {response}")


# Create API
metaplex_api = MetaplexAPI(cfg)

# Deploy
print("About to deploy")
response = metaplex_api.deploy(api_endpoint, "A" * 32, "A" * 10, 0)
"""
'{"status": 200, "contract": "7bxe7t1aGdum8o97bkuFeeBTcbARaBn9Gbv5sBd9DZPG", "msg": "Successfully created mint 7bxe7t1aGdum8o97bkuFeeBTcbARaBn9Gbv5sBd9DZPG", "tx": "2qmiWoVi2PNeAjppe2cNbY32zZCJLXMYgdS1zRVFiKJUHE41T5b1WfaZtR2QdFJUXadrqrjbkpwRN5aG2J3KQrQx"}'
"""
print(f"response: {response}")
contract = json.loads(response)["contract"]

# 6evVVcab5Qsk67tDLgAdCWUcUj6K6fnVSaUCzgbFFyhA

# Topup - The base58 encoded public key of the destination address
RECEIVER_PUBLIC_KEY = "7hLeJJUYmp42WEhZamd1XwgoTFj2pyZe9RG685ogi9fb"
metaplex_api.topup(api_endpoint, PublicKey.from_string(RECEIVER_PUBLIC_KEY))

# Mint
print("About to mint")
"""
contract_key: (str) The base58 encoded public key of the mint address
dest_key: (str) The base58 encoded public key of the destinaion address (where the contract will be minted)
link: (str) The link to the content of the the NFT
"""
metaplex_api.mint(
    api_endpoint,
    PublicKey.from_string(contract),
    PublicKey.from_string(RECEIVER_PUBLIC_KEY),
    "https://ipfs.io/ipfs/bafkreidr5cnmualj2eh7g6bpe2iztglbfvottfceamswqevlye7negmkcq",
)

# Send
"""
contract_key: (str) The base58 encoded public key of the mint address
sender_key: (str) The base58 encoded public key of the source address (from which the contract will be transferred)
dest_key: (str) The base58 encoded public key of the destinaion address (to where the contract will be transferred)
encrypted_private_key: (bytes) The encrypted private key of the sender
"""
encrypted_key = metaplex_api.cipher.encrypt(
    bytes(
        [
            95,
            46,
            174,
            145,
            248,
            101,
            108,
            111,
            128,
            44,
            41,
            212,
            118,
            145,
            42,
            242,
            84,
            6,
            31,
            115,
            18,
            126,
            47,
            230,
            103,
            202,
            46,
            7,
            194,
            149,
            42,
            213,
        ]
    )
)
metaplex_api.send(
    api_endpoint,
    contract,
    PublicKey.from_string(PUBLIC_KEY),
    PublicKey.from_string(RECEIVER_PUBLIC_KEY),
    encrypted_key,
)
