from bitcoin_client.ledger_bitcoin import Client, AddressType, MultisigWallet, PolicyMapWallet
from bitcoin_client.ledger_bitcoin.exception.errors import IncorrectDataError


import pytest

# TODO: add tests with UI


def test_get_wallet_address_singlesig_legacy(client: Client):
    # legacy address (P2PKH)
    wallet = PolicyMapWallet(
        name="",
        policy_map="pkh(@0)",
        keys_info=[
            f"[1fedcf9d/1129/0/0]tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas/**",
        ],
    )
    addr1 = client.get_wallet_address(wallet, None, 0,  0, False) 
    addr2 = client.get_wallet_address(wallet, None, 1, 15, False)
    assert addr1 == "76somRhNtdfVTN7ZiFkDuFyAGGrQiGKNRy"
    assert addr2 == "73CwPbjNsGGCRy6RnWPAMbAAGxb398v5Qk"


def test_get_wallet_address_singlesig_wit(client: Client):
    # bech32 address (P2WPKH)
    wallet = PolicyMapWallet(
        name="",
        policy_map="wpkh(@0)",
        keys_info=[
             f"[1fedcf9d/1129/0/0]tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas/**",
        ],
    )
    addr1 = client.get_wallet_address(wallet, None, 0,  0, False) 
    addr2 = client.get_wallet_address(wallet, None, 1, 15, False)
    assert addr1 == "tf1q98qremcr7szvya8rk9cx6w9ek2j799fqxfulah"
    assert addr2 == "tf1qq9lqpzrhekz74mx804j49p8dsxx38cy2tmtm3j"


def test_get_wallet_address_singlesig_sh_wit(client: Client):
    # wrapped segwit addresses (P2SH-P2WPKH)
    wallet = PolicyMapWallet(
        name="",
        policy_map="sh(wpkh(@0))",
        keys_info=[
             f"[1fedcf9d/1129/0/0]tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas/**",
        ],
    )
    addr1 = client.get_wallet_address(wallet, None, 0,  0, False) 
    addr2 = client.get_wallet_address(wallet, None, 1, 15, False)
    assert addr1 == "ttVsXXFuVM7B2DCC2tiMUbGt3BPV2xbNxF"
    assert addr2 == "tYojXT4ZD1WmYpZAccDNi1efApHL69gtsu"


def test_get_wallet_address_singlesig_taproot(client: Client):
    # test for a native taproot wallet (bech32m addresses, per BIP-0086)

    wallet = PolicyMapWallet(
        name="",
        policy_map="tr(@0)",
        keys_info=[
            f"[1fedcf9d/1129/0/0]tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas/**",
        ],
    )

    res = client.get_wallet_address(wallet, None, 0, 0, False)
    assert res == "tf1p289hh3ygz3pn97vgvrqfn92xj85sgj77umy7e77gw00mzw230lzsxkcyps"

    res = client.get_wallet_address(wallet, None, 0, 9, False)
    assert res == "tf1pda3hswntt84vhnz8waugjqfa2l7hutcug8dccptqr0kay4pe8pesmqgvdn"

    res = client.get_wallet_address(wallet, None, 1, 0, False)
    assert res == "tf1ptupfmyzmy3u2tfj472cd0mty54yxmk86y5k32kfpjgrxpt4jwmuqptefwt"

    res = client.get_wallet_address(wallet, None, 1, 9, False)
    assert res == "tf1p78r2ruex7qfzgwt3xsgmjzlm05nhquufh0xvh9ue8kw6h3mngf3sn3xrr7"


# Failure cases for default wallets

def test_get_wallet_address_default_fail_wrongkeys(client: Client):
    # 0 keys info should be rejected
    with pytest.raises(IncorrectDataError):
        client.get_wallet_address(PolicyMapWallet(
            name="",
            policy_map="pkh(@0)",
            keys_info=[],
        ), None, 0,  0, False)

    # more than 1 key should be rejected
    with pytest.raises(IncorrectDataError):
        client.get_wallet_address(PolicyMapWallet(
            name="",
            policy_map="pkh(@0)",
            keys_info=[
                f"[1fedcf9d/1129/0/0]tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas/**",
                 f"[1fedcf9d/1129/0/0]tpubDCUQMWxnQyKsdANnL9GdJ2JhjhEmRW6GKNN4nffbsGTtE33Mp2E5pf99i4TPPaweLYfmQxY39TL76eVkRYxY4E8LAT3jHR5pmFKdzpmKXas/**",
            ],
        ), None, 0,  0, False)

    # wrong BIP44 purpose should be rejected (here using 84' for a P2PKH address)
    with pytest.raises(IncorrectDataError):
        client.get_wallet_address(PolicyMapWallet(
            name="",
            policy_map="pkh(@0)",
            keys_info=[
                f"[1fedcf9d/84'/1'/0']tpubDCtKfsNyRhULjZ9XMS4VKKtVcPdVDi8MKUbcSD9MJDyjRu1A2ND5MiipozyyspBT9bg8upEp7a8EAgFxNxXn1d7QkdbL52Ty5jiSLcxPt1P/**",
            ],
        ), None, 0,  0, False)

    # mismatching pubkey (claiming key origin "44'/1'/0'", but that's the extended dpubkey for "84'/1'/0'"")
    with pytest.raises(IncorrectDataError):
        client.get_wallet_address(PolicyMapWallet(
            name="",
            policy_map="pkh(@0)",
            keys_info=[
                f"[1fedcf9d/44'/1'/0']tpubDCtKfsNyRhULjZ9XMS4VKKtVcPdVDi8MKUbcSD9MJDyjRu1A2ND5MiipozyyspBT9bg8upEp7a8EAgFxNxXn1d7QkdbL52Ty5jiSLcxPt1P/**",
            ],
        ), None, 0,  0, False)

    # wrong master fingerprint
    with pytest.raises(IncorrectDataError):
        client.get_wallet_address(PolicyMapWallet(
            name="",
            policy_map="pkh(@0)",
            keys_info=[
                f"[42424242/44'/1'/0']tpubDCwYjpDhUdPGP5rS3wgNg13mTrrjBuG8V9VpWbyptX6TRPbNoZVXsoVUSkCjmQ8jJycjuDKBb9eataSymXakTTaGifxR6kmVsfFehH1ZgJT/**",
            ],
        ), None, 0,  0, False)

    # too large address_index, cannot be done non-silently
    with pytest.raises(IncorrectDataError):
        client.get_wallet_address(PolicyMapWallet(
            name="",
            policy_map="pkh(@0)",
            keys_info=[
                f"[f5acc2fd/44'/1'/0']tpubDCwYjpDhUdPGP5rS3wgNg13mTrrjBuG8V9VpWbyptX6TRPbNoZVXsoVUSkCjmQ8jJycjuDKBb9eataSymXakTTaGifxR6kmVsfFehH1ZgJT/**",
            ],
        ), None, 0,  100000, False)