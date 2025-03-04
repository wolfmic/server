"""
Coturn static auth api

Creates ice_server record with temporary credentials computed from coturn static-auth-secret

http://stackoverflow.com/a/35767224
"""

import base64
import hmac
import time
from hashlib import sha1

from server.config import config


class CoturnHMAC:
    def __init__(self, coturn_hosts=[], coturn_keys=[]):
        self.coturn_hosts = coturn_hosts
        self.coturn_keys = coturn_keys

    def server_tokens(self, username="faf-user", ttl=None) -> list[dict[str]]:
        if ttl is None:
            ttl = config.TWILIO_TTL  # pragma: no cover

        servers = []

        # See https://github.com/coturn/coturn/wiki/turnserver#turn-rest-api
        # create hmac of coturn_key + timestamp:username
        timestamp = int(time.time()) + ttl
        token_name = f"{timestamp}:{username}"

        for coturn_host, coturn_key in zip(
            self.coturn_hosts, self.coturn_keys
        ):
            secret = hmac.new(
                coturn_key.encode(),
                str(token_name).encode(), sha1
            )
            auth_token = base64.b64encode(secret.digest()).decode()

            servers.append({
                "urls": [
                    f"turn:{coturn_host}?transport=tcp",
                    f"turn:{coturn_host}?transport=udp",
                    f"stun:{coturn_host}",
                ],
                "username": token_name,
                "credential": auth_token,
                "credentialType": "token",
            })

        return servers
