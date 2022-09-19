from bitcoin_client.ledger_bitcoin import Client


def test_get_master_fingerprint(client: Client):
    master_fingerprint = client.get_master_fingerprint()
    assert master_fingerprint == b'\x1f\xed\xcf\x9d'
