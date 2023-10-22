import json
from cryptography.fernet import Fernet
import base58
from solders.keypair import Keypair
from metaplex.transactions import deploy, topup, mint, send, burn, update_token_metadata
from utils.execution_engine import execute


class MetaplexAPI:
    def __init__(self, cfg):
        self.private_key = base58.b58decode(cfg["PRIVATE_KEY"])
        self.public_key = cfg["PUBLIC_KEY"]
        self.keypair = Keypair.from_bytes(
            [
                218,
                164,
                132,
                47,
                55,
                43,
                133,
                244,
                135,
                225,
                132,
                168,
                68,
                252,
                24,
                202,
                27,
                65,
                170,
                8,
                26,
                118,
                247,
                203,
                58,
                182,
                166,
                10,
                234,
                173,
                109,
                255,
                138,
                157,
                41,
                152,
                195,
                236,
                147,
                215,
                23,
                133,
                123,
                187,
                41,
                38,
                27,
                188,
                15,
                59,
                249,
                191,
                39,
                209,
                201,
                213,
                175,
                12,
                248,
                78,
                196,
                119,
                78,
                225,
            ]
        )
        self.cipher = Fernet(cfg["DECRYPTION_KEY"])

    def wallet(self):
        """Generate a wallet and return the address and private key."""
        keypair = Keypair()
        pub_key = keypair.pubkey
        private_key = list(keypair.seed)
        return json.dumps({"address": str(pub_key), "private_key": private_key})

    def deploy(
        self,
        api_endpoint,
        name,
        symbol,
        fees,
        max_retries=1,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
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
            return json.dumps({"contract": contract, "status": 200})
        except:
            return json.dumps({"status": 400})

    def topup(
        self,
        api_endpoint,
        to,
        amount=None,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
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
            return resp.to_json()
        except:
            return json.dumps({"status": 400})

    def mint(
        self,
        api_endpoint,
        contract_key,
        dest_key,
        link,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
        supply=1,
    ):
        """
        Mints an NFT to an account, updates the metadata and creates a master edition
        """
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
        return resp.to_json()
        # except:
        #     return json.dumps({"status": 400})

    def update_token_metadata(
        self,
        api_endpoint,
        mint_token_id,
        link,
        data,
        creators_addresses,
        creators_verified,
        creators_share,
        fee,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
        supply=1,
    ):
        """
        Updates the json metadata for a given mint token id.
        """
        tx, signers = update_token_metadata(
            api_endpoint,
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
        resp["status"] = 200
        return json.dumps(resp)

    def send(
        self,
        api_endpoint,
        contract_key,
        sender_key,
        dest_key,
        encrypted_private_key,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
        """
        Transfer a token on a given network and contract from the sender to the recipient.
        May require a private key, if so this will be provided encrypted using Fernet: https://cryptography.io/en/latest/fernet/
        Return a status flag of success or fail and the native transaction data.
        """
        try:
            private_key = list(self.cipher.decrypt(encrypted_private_key))
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
            resp["status"] = 200
            return json.dumps(resp)
        except:
            return json.dumps({"status": 400})

    def burn(
        self,
        api_endpoint,
        contract_key,
        owner_key,
        encrypted_private_key,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
        """
        Burn a token, permanently removing it from the blockchain.
        May require a private key, if so this will be provided encrypted using Fernet: https://cryptography.io/en/latest/fernet/
        Return a status flag of success or fail and the native transaction data.
        """
        try:
            private_key = list(self.cipher.decrypt(encrypted_private_key))
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
            resp["status"] = 200
            return json.dumps(resp)
        except:
            return json.dumps({"status": 400})
