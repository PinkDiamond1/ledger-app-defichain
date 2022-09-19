from bitcoin_client.bitcoin_base_cmd import AddrType


def test_get_public_key(cmd):
    # legacy address
    pub_key, addr, bip32_chain_code = cmd.get_public_key(
        addr_type=AddrType.Legacy,
        bip32_path="129/0/0/0",
        display=False
    )

    assert pub_key == b'\x04\xb6[$\xcf\xdf4\xd6\xab\xc1$\x96i4\x94\xf0\x96\xab9.AGO/mV\xd8\xbb\xb8\xb3o\xae0_z\x88_\x85!\x11\xbf\xf2\xd6h\x8d\x17_\xa3|)3\xe7\xf1b\xdd\x8c6\xbc\x16L\x83\xc7t\xc5\xab'
    assert addr == "76uNViagz7L2UmsioFAifnZnfZ2NBtnhzT"
    assert bip32_chain_code == b'\xe6\x8c\x10z$\xa3\xae\xcb4\xd2\x01\x89]\xa3\x8e\xd5\xe4>\xbb\x90 \x9c9~\xe1\xbd;\xe7\x9b\xfdl8'

