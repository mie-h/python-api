from typing import Any, Optional
import struct
from enum import IntEnum
from construct import Bytes, Flag, Int8ul
from construct import Struct as cStruct  # type: ignore
from solders.pubkey import Pubkey as PublicKey
from solders.instruction import Instruction
from solana.rpc.api import Client
from solana.transaction import AccountMeta
import base58

MAX_NAME_LENGTH = 32
MAX_SYMBOL_LENGTH = 10
MAX_URI_LENGTH = 200
MAX_CREATOR_LENGTH = 34
MAX_CREATOR_LIMIT = 5


class InstructionType(IntEnum):
    CREATE_METADATA = 0
    UPDATE_METADATA = 1


METADATA_PROGRAM_ID = PublicKey.from_string(
    "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
)
SYSTEM_PROGRAM_ID = PublicKey.from_string("11111111111111111111111111111111")
SYSVAR_RENT_PUBKEY = PublicKey.from_string(
    "SysvarRent111111111111111111111111111111111"
)
ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID = PublicKey.from_string(
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
)
TOKEN_PROGRAM_ID = PublicKey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")


def get_metadata_account(mint_key: PublicKey) -> PublicKey:
    return PublicKey.find_program_address(
        [
            b"metadata",
            METADATA_PROGRAM_ID.__bytes__(),
            mint_key.__bytes__(),
        ],
        METADATA_PROGRAM_ID,
    )[0]


def get_edition(mint_key: PublicKey) -> PublicKey:
    return PublicKey.find_program_address(
        [
            b"metadata",
            METADATA_PROGRAM_ID.__bytes__(),
            mint_key.__bytes__(),
            b"edition",
        ],
        METADATA_PROGRAM_ID,
    )[0]


def create_associated_token_account_instruction(
    associated_token_account: PublicKey, payer: PublicKey, wallet_address: PublicKey, token_mint_address: PublicKey
) -> Instruction:
    keys = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=associated_token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=wallet_address, is_signer=False, is_writable=False),
        AccountMeta(pubkey=token_mint_address, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    arbitrary_instruction_data = bytes([1])
    instruction = Instruction(
        ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID, arbitrary_instruction_data, keys
    )
    return instruction


def _get_data_buffer(name: str, symbol: str, uri: str, fee: int, creators: list[bytes], verified: Optional[list[int]] = None, share: Optional[list[int]] = None) -> bytes:
    if isinstance(share, list):
        assert len(share) == len(creators)
    if isinstance(verified, list):
        assert len(verified) == len(creators)
    args = [
        len(name),
        *list(name.encode()),
        len(symbol),
        *list(symbol.encode()),
        len(uri),
        *list(uri.encode()),
        fee,
    ]

    byte_fmt = "<"
    byte_fmt += "I" + "B" * len(name)
    byte_fmt += "I" + "B" * len(symbol)
    byte_fmt += "I" + "B" * len(uri)
    byte_fmt += "h"
    byte_fmt += "B"
    if creators:
        args.append(1)
        byte_fmt += "I"
        args.append(len(creators))
        for i, creator in enumerate(creators):
            byte_fmt += "B" * 32 + "B" + "B"
            args.extend(list(base58.b58decode(creator)))
            if isinstance(verified, list):
                args.append(verified[i])
            else:
                args.append(1)
            if isinstance(share, list):
                args.append(share[i])
            else:
                args.append(100)
    else:
        args.append(0)
    buffer = struct.pack(byte_fmt, *args)
    return buffer


def create_metadata_instruction_data(name: str, symbol: str, fee: int, creators: list[bytes]) -> bytes:
    _data = _get_data_buffer(name, symbol, " " * 64, fee, creators)
    metadata_args_layout = cStruct(
        "data" / Bytes(len(_data)),
        "is_mutable" / Flag,
    )
    _create_metadata_args = dict(data=_data, is_mutable=True)
    instruction_layout = cStruct(
        "instruction_type" / Int8ul,
        "args" / metadata_args_layout,
    )
    return instruction_layout.build(
        dict(
            instruction_type=InstructionType.CREATE_METADATA,
            args=_create_metadata_args,
        )
    )


def create_metadata_instruction(
    data: bytes, update_authority: PublicKey, mint_key: PublicKey, mint_authority_key: PublicKey, payer: PublicKey
) -> Instruction:
    metadata_account = get_metadata_account(mint_key)
    keys = [
        AccountMeta(pubkey=metadata_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint_key, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint_authority_key, is_signer=True, is_writable=False),
        AccountMeta(pubkey=payer, is_signer=True, is_writable=False),
        AccountMeta(pubkey=update_authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]

    return Instruction(METADATA_PROGRAM_ID, data, keys)


def unpack_metadata_account(data: bytes) -> dict[str, Any]:
    assert data[0] == 4
    i = 1
    source_account = base58.b58encode(
        bytes(struct.unpack("<" + "B" * 32, data[i : i + 32]))
    )
    i += 32
    mint_account = base58.b58encode(
        bytes(struct.unpack("<" + "B" * 32, data[i : i + 32]))
    )
    i += 32
    name_len = struct.unpack("<I", data[i : i + 4])[0]
    i += 4
    name = struct.unpack("<" + "B" * name_len, data[i : i + name_len])
    i += name_len
    symbol_len = struct.unpack("<I", data[i : i + 4])[0]
    i += 4
    symbol = struct.unpack("<" + "B" * symbol_len, data[i : i + symbol_len])
    i += symbol_len
    uri_len = struct.unpack("<I", data[i : i + 4])[0]
    i += 4
    uri = struct.unpack("<" + "B" * uri_len, data[i : i + uri_len])
    i += uri_len
    fee = struct.unpack("<h", data[i : i + 2])[0]
    i += 2
    has_creator = data[i]
    i += 1
    creators = []
    verified = []
    share = []
    if has_creator:
        creator_len = struct.unpack("<I", data[i : i + 4])[0]
        i += 4
        for _ in range(creator_len):
            creator = base58.b58encode(
                bytes(struct.unpack("<" + "B" * 32, data[i : i + 32]))
            )
            creators.append(creator)
            i += 32
            verified.append(data[i])
            i += 1
            share.append(data[i])
            i += 1
    primary_sale_happened = bool(data[i])
    i += 1
    is_mutable = bool(data[i])
    metadata = {
        "update_authority": source_account,
        "mint": mint_account,
        "data": {
            "name": bytes(name).decode("utf-8").strip("\x00"),
            "symbol": bytes(symbol).decode("utf-8").strip("\x00"),
            "uri": bytes(uri).decode("utf-8").strip("\x00"),
            "seller_fee_basis_points": fee,
            "creators": creators,
            "verified": verified,
            "share": share,
        },
        "primary_sale_happened": primary_sale_happened,
        "is_mutable": is_mutable,
    }
    return metadata


def get_metadata(client: Client, mint_key: PublicKey) -> dict[str, Any]:
    metadata_account = get_metadata_account(mint_key)
    account_info = client.get_account_info(metadata_account)
    account = account_info.value
    if account is None:
        return {}
    metadata = unpack_metadata_account(account.data)
    return metadata


def update_metadata_instruction_data(name: str, symbol: str, uri: str, fee: int, creators: list[bytes], verified: list[int], share: list[int]) -> bytes:
    _data = (
        bytes([1])
        + _get_data_buffer(name, symbol, uri, fee, creators, verified, share)
        + bytes([0, 0])
    )
    instruction_layout = cStruct(
        "instruction_type" / Int8ul,
        "args" / Bytes(len(_data)),
    )
    return instruction_layout.build(
        dict(
            instruction_type=InstructionType.UPDATE_METADATA,
            args=_data,
        )
    )


def update_metadata_instruction(data: bytes, update_authority: PublicKey, mint_key: PublicKey) -> Instruction:
    metadata_account = get_metadata_account(mint_key)
    keys = [
        AccountMeta(pubkey=metadata_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=update_authority, is_signer=True, is_writable=False),
    ]
    return Instruction(METADATA_PROGRAM_ID, data, keys)


def create_master_edition_instruction(
    mint: PublicKey,
    update_authority: PublicKey,
    mint_authority: PublicKey,
    payer: PublicKey,
    supply: Optional[int],
) -> Instruction:
    edition_account = get_edition(mint)
    metadata_account = get_metadata_account(mint)
    if supply is None:
        data = struct.pack("<BB", 10, 0)
    else:
        data = struct.pack("<BBQ", 10, 1, supply)
    keys = [
        AccountMeta(pubkey=edition_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=True),
        AccountMeta(pubkey=update_authority, is_signer=True, is_writable=False),
        AccountMeta(pubkey=mint_authority, is_signer=True, is_writable=False),
        AccountMeta(pubkey=payer, is_signer=True, is_writable=False),
        AccountMeta(pubkey=metadata_account, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False
        ),
    ]
    return Instruction(METADATA_PROGRAM_ID, data, keys)
