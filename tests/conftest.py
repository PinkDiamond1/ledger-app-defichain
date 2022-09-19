import random
import binascii
import hashlib
import string
import random
from typing import Tuple

from test_utils.fixtures import *
from test_utils.authproxy import AuthServiceProxy, JSONRPCException
from test_utils import segwit_addr

import shutil
import subprocess
from time import sleep
from decimal import Decimal

import bitcoin_client.ledger_bitcoin._base58 as base58
from bitcoin_client.ledger_bitcoin.common import sha256

random.seed(0)  # make sure tests are repeatable

# Make sure that the native client library is used with, as speculos would otherwise
# return a version number < 2.0.0 for the app
os.environ['SPECULOS_APPNAME'] = f'DeFiChain Test:{get_app_version()}'


DEFICHAIN_DIRNAME = os.getenv("DEFICHAIN_DIRNAME", ".test_bitcoin")


rpc_url = "http://%s:%s@%s:%s" % (
    os.getenv("DFI_RPC_USER", "user"),
    os.getenv("DFI_RPC_PASSWORD", "passwd"),
    os.getenv("DFI_RPC_HOST", "127.0.0.1"),
    os.getenv("DFI_RPC_PORT", "18443")
)

utxos = list()
btc_addr = ""


def get_rpc() -> AuthServiceProxy:
    return AuthServiceProxy(rpc_url)


def get_wallet_rpc(wallet_name: str) -> AuthServiceProxy:
    return AuthServiceProxy(f"{rpc_url}/wallet/{wallet_name}")


def setup_node():
    global dfi_addr
    letters = string.ascii_lowercase
    global wallet_name 
    wallet_name = ''.join(random.choice(letters) for i in range(20))

    # Check defid is running while generating the address
    while True:
        rpc = get_wallet_rpc(wallet_name)
        try:
            rpc.createwallet(wallet_name=wallet_name)
            dfi_addr = rpc.getnewaddress()
            break

        except ConnectionError as e:
            sleep(1)
        except JSONRPCException as e:
            wallet_name = ''.join(random.choice(letters) for i in range(20))
            if "Loading wallet..." in str(e):
                sleep(1)
            print(e);

    print("wallet setup...")

    print(rpc.importprivkey("cRiRQ9cHmy5evDqNDdEV8f6zfbK6epi9Fpz4CRZsmLEmkwy54dWz", "operator", True))
    print(rpc.importprivkey("cPGEaz8AGiM71NGMRybbCqFNRcuUhg3uGvyY4TFE1BZC26EW2PkC", "owner", True))
    # Mine enough blocks so coinbases are mature and we have enough funds to run everything
    rpc.generatetoaddress(105, "mswsMVsyGMj1FzDMbbxw2QW3KvQAv2FKiy", 1)


@pytest.fixture(scope="session")
def run_defid():
    # Run defid in a separate folder
    os.makedirs(DEFICHAIN_DIRNAME, exist_ok=True)

    defid = os.getenv("defid", "defid")

    print(os.getenv("PATH"))

    print("starting defid")
    shutil.copy(os.path.join(os.path.dirname(__file__), "defi.conf"), DEFICHAIN_DIRNAME)
    subprocess.Popen([defid, f"--datadir={DEFICHAIN_DIRNAME}", f"-txindex", "-regtest", "-printtoconsole", "-jellyfish_regtest=1", "-txnotokens=0", "-logtimemicros", "-txindex=1", "-acindex=1", "-amkheight=0", "-bayfrontheight=1", "-bayfrontgardensheight=2", "-clarkequayheight=3", "-dakotaheight=4", "-dakotacrescentheight=5", "-eunosheight=6", "-eunospayaheight=7", "-fortcanningheight=8", "-fortcanningmuseumheight=9", "-fortcanninghillheight=10", "-fortcanningroadheight=11", "-fortcanningcrunchheight=12", "-fortcanningspringheight=13", "-dummypos=0", "-spv=1", "-anchorquorum=2", "-masternode_operator=mswsMVsyGMj1FzDMbbxw2QW3KvQAv2FKiy"])
    print("started defid")

    # Make sure the node is ready, and generate some initial blocks
    setup_node()

    yield

    rpc = get_rpc()
    rpc.stop()

    shutil.rmtree(DEFICHAIN_DIRNAME)


@pytest.fixture(scope="session")
def rpc(run_defid):
    return get_rpc()


@pytest.fixture(scope="session")
def rpc_test_wallet(run_defid):
    return get_wallet_rpc("test_wallet")


def get_utxo():
    rpc = get_rpc()
    global utxos
    if not utxos:
        utxos = rpc.listunspent()

    if len(utxos) == 0:
        raise ValueError("There are no UTXOs.")

    utxo = utxos.pop(0)
    while utxo.get("amount") < Decimal("0.00002"):
        utxo = utxos.pop(0)

    return utxo


def seed_to_wif(seed: bytes):
    assert len(seed) == 32

    double_sha256 = sha256(sha256(b"\x80" + seed))
    return base58.encode(b"\x80" + seed + double_sha256[:4])


wallet_count = 0


def get_unique_wallet_name() -> str:
    global wallet_count

    result = f"mywallet-{wallet_count}"

    wallet_count += 1

    return result


def create_new_wallet() -> Tuple[str, str]:
    """Creates a new descriptor-enabled wallet in bitcoin-core. Each new wallet has an increasing counter as
    part of it's name in order to avoid conflicts."""

    wallet_name = get_unique_wallet_name()

    # TODO: derive seed from wallet_count, and use it to create a descriptor wallet (how?)
    #       this would help to have repeatable tests, generating always the same seeds

    get_rpc().createwallet(wallet_name=wallet_name, descriptors=True)
    wallet_rpc = get_wallet_rpc(wallet_name)

    descriptor: str = next(filter(lambda d: d["desc"].startswith(
        "pkh"), wallet_rpc.listdescriptors()["descriptors"]))["desc"]
    core_xpub_orig = descriptor[descriptor.index("(")+1: descriptor.index("/0/*")]

    return wallet_name, core_xpub_orig


def generate_blocks(n):
    return get_rpc().generatetoaddress(n, btc_addr)


def testnet_to_regtest_addr(addr: str) -> str:
    """Convenience function to reencode addresses from testnet format to regtest one (bech32 prefix is different)"""
    hrp, data, spec = segwit_addr.bech32_decode(addr)
    if hrp is None:
        return addr  # bech32m decoding failed; either legacy/unknown address type, or invalid address
    if (hrp != "tb"):
        raise ValueError("Not a valid testnet bech32m string")
    return segwit_addr.bech32_encode("bcrt", data, spec)
