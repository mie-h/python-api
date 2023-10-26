import time
from typing import Optional
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.rpc.responses import SendTransactionResp
from solders.signature import Signature
from solders.transaction_status import TransactionConfirmationStatus


def execute(
    api_endpoint: str,
    tx: Transaction,
    signers: list[Keypair],
    max_retries: int = 1,
    skip_confirmation: bool = False,
    max_timeout: int = 60,
    target: int = 20,
    finalized: bool = True,
) -> Optional[SendTransactionResp]:
    client = Client(api_endpoint)
    for attempt in range(max_retries):
        try:
            result = client.send_transaction(
                tx, *signers, opts=TxOpts(skip_confirmation=False, skip_preflight=True)
            )
            signatures = [x for x in tx.signatures]
            if not skip_confirmation:
                await_confirmation(client, signatures, max_timeout, target, finalized)
            return result
        except Exception as e:
            print(f"Failed attempt {attempt}: {e}")
            continue
    return None


def await_confirmation(
    client: Client, signatures: list[Signature], max_timeout: int = 60, target: int = 20, finalized: bool = True
) -> None:
    elapsed = 0
    while elapsed < max_timeout:
        sleep_time = 1
        time.sleep(sleep_time)
        elapsed += sleep_time
        resp = client.get_signature_statuses(signatures)
        if resp.value[0] is not None:
            confirmations = resp.value[0].confirmations
            is_finalized = (
                resp.value[0].confirmation_status
                == TransactionConfirmationStatus.Finalized
            )
        else:
            continue
        if not finalized:
            if confirmations is not None and confirmations >= target or is_finalized:
                print(f"Took {elapsed} seconds to confirm transaction")
                return
        elif is_finalized:
            print(f"Took {elapsed} seconds to confirm transaction")
            return
