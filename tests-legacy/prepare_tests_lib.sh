#!/bin/bash
bash ./clean_tests.sh

# TODO: tests currently not working with DEBUG=1

cd ..
make clean
make -j DEBUG=0 COIN=defichain
mv bin/ tests-legacy/defichain-bin
make clean
make -j DEBUG=0 COIN=defichain_testnet_lib
mv bin/ tests-legacy/defichain-testnet-bin
