# An image derived from ledgerhq/speculos but also containing the bitcoin-core binaries

FROM ghcr.io/ledgerhq/speculos:latest

# install curl
RUN apt update -y && apt install -y curl

# download defichain-core and decompress it to /defichain
RUN curl -o /tmp/defichain.tar.gz https://github.com/DeFiCh/ain/releases/download/v2.9.4/defichain-2.9.4-x86_64-pc-linux-gnu.tar.gz && \
    tar -xf /tmp/defichain.tar.gz -C / && \
    mv /defichain-22.0 /defichain

# Add bitcoin binaries to path
ENV PATH=/defichain/bin:$PATH
