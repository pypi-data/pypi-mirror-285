import re
from typing import NamedTuple

RX_PROXY_URI = r"^(https?\:\/\/)(?:([^:@]+):([^@]+)@)?([^:@]+):([^:@]+)$"


class ProxyURI(NamedTuple):
    uri: str
    protocol: str
    username: str
    password: str
    host: str
    port: str
    server: str

    @staticmethod
    def new(uri: str):
        if uri == None:
            return None

        match = re.search(RX_PROXY_URI, uri)

        if match == None:
            return None

        protocol = match[1]
        username = match[2]
        password = match[3]
        host = match[4]
        port = match[5]
        server = f"{protocol}{host}:{port}"

        return ProxyURI(
            uri=uri,
            protocol=protocol,
            username=username,
            password=password,
            host=host,
            port=port,
            server=server,
        )

    @staticmethod
    def new_dict(
        uri: str,
        remove_empty=True,
    ):
        proxy = ProxyURI.new(uri)

        if proxy == None:
            return None

        result = proxy._asdict()

        if not remove_empty:
            return result

        items = result.items()

        return {k: v for k, v in items if v != None}
