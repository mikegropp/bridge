import click
import secrets
from chia.util.keychain import bytes_to_mnemonic, mnemonic_to_seed
from chia.wallet.derive_keys import _derive_path, master_sk_to_wallet_sk_unhardened
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import calculate_synthetic_public_key, DEFAULT_HIDDEN_PUZZLE_HASH, puzzle_hash_for_synthetic_public_key
from chia_rs import AugSchemeMPL, PrivateKey
from chia.util.bech32m import encode_puzzle_hash
from commands.config import get_config_item
from eth_account import Account
from web3.auto import w3

@click.group()
def keys():
    pass

def mnemonic_to_validator_pk(mnemonic: str) -> PrivateKey:
    seed = mnemonic_to_seed(mnemonic)
    root_key = AugSchemeMPL.key_gen(seed)
    return _derive_path(root_key, [12381, 8444, 7, 0])

@keys.command()
def generate_xch_key():
    click.echo("Generating XCH key...")
    entropy = secrets.token_bytes(16)
    mnemonic = bytes_to_mnemonic(entropy)
    click.echo(f"Mnemonic: {mnemonic}")
    private_key = mnemonic_to_validator_pk(mnemonic)
    public_key = private_key.get_g1()
    click.echo(f"Private Key: {bytes(private_key).hex()}")
    click.echo(f"Public Key: {public_key}")

    seed = mnemonic_to_seed(mnemonic)
    root_key = AugSchemeMPL.key_gen(seed)
    private_key = _derive_path(root_key, [12381, 8444, 7, 0])
    first_wallet_sk = master_sk_to_wallet_sk_unhardened(root_key, 0)
    first_wallet_pk = first_wallet_sk.get_g1()
    first_wallet_synthetic_key = calculate_synthetic_public_key(first_wallet_pk, DEFAULT_HIDDEN_PUZZLE_HASH)
    first_puzzle_hash = puzzle_hash_for_synthetic_public_key(first_wallet_synthetic_key)
    first_address = encode_puzzle_hash(first_puzzle_hash, get_config_item(["xch", "prefix"]))
    click.echo(f"First address: {first_address}")

@keys.command()
def generate_eth_key():
    click.echo("Generating ETH key...")

    account = Account.create()

    click.echo(f"Private Key: {account.key.hex()}")
    click.echo(f"Public Key: {account._key_obj.public_key}")
    click.echo(f"Address: {w3.to_checksum_address(account.address)}")
