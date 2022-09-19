import threading

import pytest

from bitcoin_client.ledger_bitcoin import Client
from bitcoin_client.ledger_bitcoin.exception import DenyError, NotSupportedError
from speculos.client import SpeculosClient


def test_get_extended_pubkey_nonstandard_nodisplay(client: Client):
    # as these paths are not standard, the app should reject immediately if display=False
    testcases = [
        "m",  # unusual to export the root key
        "m/44'",
        "m/44'/1'",
        "m/44'/10'/0'",  # wrong coin_type
        "m/44'/1'/0",  # first step should be hardened
        "m/44'/1/0'",  # second step should be hardened
        "m/44/1'/0'",  # third step should be hardened
        "m/48'/1'/0'/0'",  # script_type is 1' or 2' for BIP-0048
        "m/48'/1'/0'/3'",  # script_type is 1' or 2' for BIP-0048
        "m/999'/1'/0'",  # no standard with this purpose
        "m/44'/1'/10'/0",  # missing address_index
        "m/44'/1'/10'/2/3",  # change bigger than 1
        "m/44'/1'/10'/0/3/5",  # no derivation steps expected after address_index
    ]

    for path in testcases:
        with pytest.raises(NotSupportedError):
            client.get_extended_pubkey(
                path=path,
                display=False
            )


def test_get_extended_pubkey_non_standard(client: Client, comm: SpeculosClient, is_speculos: bool):
    # Test the successful UX flow for a non-standard path (here, root path)
    # (Slow test, not feasible to repeat it for many paths)

    if not is_speculos:
        pytest.skip("Requires speculos")

    def ux_thread():
        event = comm.wait_for_text_event("path is unusual")

        # press right until the last screen (will press the "right" button more times than needed)
        while "Reject" != event["text"]:
            comm.press_and_release("right")

            event = comm.get_next_event()

        # go back to the Accept screen, then accept
        comm.press_and_release("left")
        comm.press_and_release("both")

    x = threading.Thread(target=ux_thread)
    x.start()

    pub_key = client.get_extended_pubkey(
        path="1129/0/0",  # root pubkey
        display=True
    )

    x.join()

    assert pub_key == "tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas"

def test_get_extended_pubkey_non_standard2(client: Client, comm: SpeculosClient, is_speculos: bool):
    # Test the successful UX flow for a non-standard path (here, root path)
    # (Slow test, not feasible to repeat it for many paths)

    if not is_speculos:
        pytest.skip("Requires speculos")

    def ux_thread():
        event = comm.wait_for_text_event("path is unusual")

        # press right until the last screen (will press the "right" button more times than needed)
        while "Reject" != event["text"]:
            comm.press_and_release("right")

            event = comm.get_next_event()

        # go back to the Accept screen, then accept
        comm.press_and_release("left")
        comm.press_and_release("both")

    x = threading.Thread(target=ux_thread)
    x.start()

    pub_key = client.get_extended_pubkey(
        path="1129/0/1",  # root pubkey
        display=True
    )

    x.join()

    assert pub_key == "tpubDCUQMWxnQyKsgWjTujJkH4zJPaazp61CpFw6pNfKd9WsS9BJxj3nhFbYBqUTr99J84FeckccgM4fFz92umVjeF8fBTcceJXCYnN1HRfumTA"


def test_get_extended_pubkey_non_standard_reject_early(client: Client, comm: SpeculosClient, is_speculos: bool):
    # Test rejecting after the "Reject if you're not sure" warning
    # (Slow test, not feasible to repeat it for many paths)

    if not is_speculos:
        pytest.skip("Requires speculos")

    def ux_thread():
        comm.wait_for_text_event("path is unusual")
        comm.press_and_release("right")
        comm.wait_for_text_event("Confirm public key")
        comm.press_and_release("right")
        comm.wait_for_text_event("111'/222'/333'")
        comm.press_and_release("right")
        comm.wait_for_text_event("not sure")  # second line of "Reject if you're not sure"
        comm.press_and_release("both")

    x = threading.Thread(target=ux_thread)
    x.start()

    with pytest.raises(DenyError):
        client.get_extended_pubkey(
            path="m/111'/222'/333'",
            display=True
        )

    x.join()


def test_get_extended_pubkey_non_standard_reject(client: Client, comm: SpeculosClient, is_speculos: bool):
    # Test rejecting at the end
    # (Slow test, not feasible to repeat it for many paths)

    if not is_speculos:
        pytest.skip("Requires speculos")

    def ux_thread():
        event = comm.wait_for_text_event("path is unusual")

        # press right until the last screen (will press the "right" button more times than needed)
        while "Reject" != event["text"]:
            comm.press_and_release("right")

            event = comm.get_next_event()

        # finally, reject
        comm.press_and_release("both")

    x = threading.Thread(target=ux_thread)
    x.start()

    with pytest.raises(DenyError):
        client.get_extended_pubkey(
            path="m/111'/222'/333'",
            display=True
        )

    x.join()
