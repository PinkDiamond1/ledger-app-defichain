from bitcoin_client.bitcoin_base_cmd import AddrType


def test_get_public_key(cmd):
    # legacy address
    pub_key, addr, bip32_chain_code = cmd.get_public_key(
        addr_type=AddrType.Legacy,
        bip32_path="m/129/0/0/0",
        display=False
    )

    assert pub_key == bytes.fromhex("04e181a1a74b7c624b3af09104c520ac6867638a43755f964401eec5fd559958074e05fbd45ec87c762c8bf12c0bf274dff675ef6593ed417acd42897827d533f9")
    assert addr == "tf1q82zscnmshac8khd8wxqxydsqx3nsnvtlm2hpnf"
    assert bip32_chain_code == bytes.fromhex("d3d1c2942c88600ca443c166e50cfc6696a809d4c4ab7a645a945578a70b5dcc")

