import base64

import requests as requests

from rudder_enrichment.environment import RUDDER_CONFIG_BACKEND_ADMIN_USERNAME, RUDDER_CONFIG_BACKEND_ADMIN_PASSWORD


class ConfigBackendClient:
    encoded_string = f"{RUDDER_CONFIG_BACKEND_ADMIN_USERNAME}:{RUDDER_CONFIG_BACKEND_ADMIN_PASSWORD}".encode('utf-8')
    encoded_header = base64.b64encode(encoded_string).decode('utf-8')

    @staticmethod
    def get(url, timeout=60):
        return requests.get(url, timeout=timeout,
                            headers={'Authorization': f'Basic {ConfigBackendClient.encoded_header}'})
