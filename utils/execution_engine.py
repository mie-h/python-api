import time
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solders.transaction_status import TransactionConfirmationStatus


def execute(
    api_endpoint,
    tx: Transaction,
    signers,
    max_retries=1,
    skip_confirmation=False,
    max_timeout=60,
    target=20,
    finalized=True,
):
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
            continue
    raise e


def await_confirmation(
    client: Client, signatures, max_timeout=60, target=20, finalized=True
):
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
            if confirmations >= target or is_finalized:
                return
        elif is_finalized:
            return
