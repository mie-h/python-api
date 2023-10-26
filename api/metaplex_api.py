import json
from typing import Any, Optional
from cryptography.fernet import Fernet
from solders.keypair import Keypair
from solders.pubkey import Pubkey as PublicKey
from metaplex.transactions import deploy, topup, mint, send, burn, update_token_metadata
from utils.execution_engine import execute


class MetaplexAPI:
    def __init__(self, cfg: dict[str, str]):
        base58_private_key = cfg["PRIVATE_KEY"] # this is base 58 encoded
        self.public_key = cfg["PUBLIC_KEY"]
        self.keypair = Keypair.from_base58_string(base58_private_key)
        self.private_key = self.keypair.to_bytes_array()
        self.cipher = Fernet(cfg["DECRYPTION_KEY"])

    def wallet(self):
        """Generate a wallet and return the address and private key."""
        keypair = Keypair()
        public_key = keypair.pubkey()
        private_key = keypair.to_bytes_array()
        return json.dumps({"address": str(public_key), "private_key": private_key})

    def deploy(
        self,
        api_endpoint: str,
        name: str,
        symbol: str,
        fees: int,
        max_retries: int = 1,
        skip_confirmation: bool = False,
        max_timeout: int = 60,
        target: int = 20,
        finalized: bool = True,
    ) -> str:
        """
        Deploy a contract to the blockchain (on network that support contracts). Takes the network ID and contract name, plus initialisers of name and symbol. Process may vary significantly between blockchains.
        Returns status code of success or fail, the contract address, and the native transaction data.
        """
        try:
            tx, signers, contract = deploy(
                api_endpoint, self.keypair, name, symbol, fees
            )
            resp = execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            if resp is None:
                raise Exception("Failed to deploy")
            return json.dumps({"contract": contract, "status": 200})
        except:
            return json.dumps({"status": 400})

    def topup(
        self,
        api_endpoint: str,
        to: str,
        amount: Optional[int]=None,
        max_retries: int = 3,
        skip_confirmation: bool = False,
        max_timeout: int = 60,
        target: int = 20,
        finalized: bool = True,
    ) -> str:
        """
        Send a small amount of native currency to the specified wallet to handle gas fees. Return a status flag of success or fail and the native transaction data.
        """
        try:
            tx, signers = topup(api_endpoint, self.keypair, to, amount=amount)
            resp = execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            if resp is None:
                raise Exception("Failed to topup")
            result: dict[str, Any] = json.loads(resp.to_json())
            result["status"] = 200
            return json.dumps(result)
        except:
            return json.dumps({"status": 400})

    def mint(
        self,
        api_endpoint: str,
        contract_key: str,
        dest_key: str,
        link: str,
        max_retries: int = 3,
        skip_confirmation: bool = False,
        max_timeout: int = 60,
        target: int = 20,
        finalized: bool = True,
        supply: int = 1,
    ) -> str:
        """
        Mints an NFT to an account, updates the metadata and creates a master edition
        """
        try:
            tx, signers = mint(
                api_endpoint, self.keypair, contract_key, dest_key, link, supply=supply
            )
            resp = execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            if resp is None:
                return json.dumps({"status": 400})
            result: dict[str, Any] = json.loads(resp.to_json())
            result["status"] = 200
            return json.dumps(result)
        except:
            return json.dumps({"status": 400})

    def update_token_metadata(
        self,
        api_endpoint: str,
        mint_token_id: str,
        link: str,
        data: dict[str, str],
        creators_addresses: list[bytes],
        creators_verified: list[int],
        creators_share: list[int],
        fee: int,
        max_retries: int = 3,
        skip_confirmation: bool = False,
        max_timeout: int = 60,
        target: int = 20,
        finalized: bool = True,
        supply: int = 1,
    ) -> str:
        """
        Updates the json metadata for a given mint token id.
        """
        try:
            tx, signers = update_token_metadata(
                self.keypair,
                mint_token_id,
                link,
                data,
                fee,
                creators_addresses,
                creators_verified,
                creators_share,
            )
            resp = execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )

            if resp is None:
                return json.dumps({"status": 400})
            result: dict[str, Any] = json.loads(resp.to_json())
            result["status"] = 200
            return json.dumps(result)
        except:
            return json.dumps({"status": 400})

    def send(
        self,
        api_endpoint: str,
        contract_key: str,
        sender_key: str,
        dest_key: str,
        encrypted_private_key: bytes,
        max_retries: int = 3,
        skip_confirmation: bool = False,
        max_timeout: int = 60,
        target: int = 20,
        finalized: bool = True,
    ) -> str:
        """
        Transfer a token on a given network and contract from the sender to the recipient.
        May require a private key, if so this will be provided encrypted using Fernet: https://cryptography.io/en/latest/fernet/
        Return a status flag of success or fail and the native transaction data.
        """
        try:
            private_key = self.cipher.decrypt(encrypted_private_key)
            tx, signers = send(
                api_endpoint,
                self.keypair,
                contract_key,
                sender_key,
                dest_key,
                private_key,
            )
            resp = execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            if resp is None:
                raise Exception("Failed to send")
            result: dict[str, Any] = json.loads(resp.to_json())
            result["status"] = 200
            return json.dumps(result)
        except:
            return json.dumps({"status": 400})

    def burn(
        self,
        api_endpoint: str,
        contract_key: str,
        owner_key: str,
        encrypted_private_key: bytes,
        max_retries: int = 3,
        skip_confirmation: bool = False,
        max_timeout: int = 60,
        target: int = 20,
        finalized: bool = True,
    ) -> str:
        """
        Burn a token, permanently removing it from the blockchain.
        May require a private key, if so this will be provided encrypted using Fernet: https://cryptography.io/en/latest/fernet/
        Return a status flag of success or fail and the native transaction data.
        """
        try:
            private_key = self.cipher.decrypt(encrypted_private_key)
            tx, signers = burn(api_endpoint, contract_key, owner_key, private_key)
            resp = execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            if resp is None:
                raise Exception("Failed to burn")
            result: dict[str, Any] = json.loads(resp.to_json())
            result["status"] = 200
            return json.dumps(result)
        except:
            return json.dumps({"status": 400})
