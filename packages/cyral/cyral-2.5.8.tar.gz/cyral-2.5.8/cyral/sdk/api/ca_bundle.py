"""Resource client to fetch CA bundle from Cyral control plane."""

import requests

from .resource import ResourceClient


class CABundleClient(ResourceClient):
    """
    CABundle resource can be used to get the CA certificate bundle used
    by a sidecar.
    """

    def get(self, sidecar_id: str, timeout: int = 5) -> str:
        "fetch CA certificate bundle"
        cp_address = self.cp_address
        url = f"https://{cp_address}/v2/sidecars/{sidecar_id}/certificate/ca"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            resp_data = resp.json()
            return resp_data.get("certificate")

        # try the legacy endpoint if the newer one did not work.
        url = f"https://{cp_address}/v1/templates/ca_bundle"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.text
