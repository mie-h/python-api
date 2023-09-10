import time
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.types import TxOpts


def execute(
    api_endpoint,
    tx,
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
            print(f"send_transaction result: {result}")
            signatures = [x.signature for x in tx.signatures]
            if not skip_confirmation:
                print("Awaiting Confirmation")
                await_confirmation(client, signatures, max_timeout, target, finalized)
            print("Done awaiting confirmation, here is the result", result)
            return result
        except Exception as e:
            print(f"Failed attempt {attempt}: {e}")
            continue
    raise e


def await_confirmation(client, signatures, max_timeout=60, target=20, finalized=True):
    elapsed = 0
    while elapsed < max_timeout:
        sleep_time = 1
        time.sleep(sleep_time)
        elapsed += sleep_time
        resp = client.get_signature_statuses(signatures)
        if resp["result"]["value"][0] is not None:
            confirmations = resp["result"]["value"][0]["confirmations"]
            is_finalized = (
                resp["result"]["value"][0]["confirmationStatus"] == "finalized"
            )
        else:
            continue
        if not finalized:
            if confirmations >= target or is_finalized:
                print(f"Took {elapsed} seconds to confirm transaction")
                return
        elif is_finalized:
            print(f"Took {elapsed} seconds to confirm transaction")
            return
