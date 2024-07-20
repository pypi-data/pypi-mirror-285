import os
import requests

def operate(operation,base_url,token,sku=None):

    if operation == "resume":

        url = f"{base_url}/resume?api-version=2022-07-01-preview"
        print(f"INFO: Calling {url}")
        response = requests.post(url, headers={'Content-Type': 'application/json', "Authorization": f"Bearer {token}"})
        if not response.ok and response.json()["error"]["message"] == 'Service is not ready to be updated':
            print(f"WARN: Service is not ready to be updated, probably it is already in desired state: {operation}")
        else:
            response.raise_for_status()

    elif operation == "suspend":

        url = f"{base_url}/suspend?api-version=2022-07-01-preview"
        print(f"INFO: Calling {url}")
        response = requests.post(url, headers={'Content-Type': 'application/json', "Authorization": f"Bearer {token}"})
        if not response.ok and response.json()["error"]["message"] == 'Service is not ready to be updated':
            print(f"WARN: Service is not ready to be updated, probably it is already in desired state: {operation}")
        else:
            response.raise_for_status()

    else:
        url = f"{base_url}?api-version=2022-07-01-preview"
        print(f"INFO: Scaling {url} to {sku}")
        payload = {"sku":{"name": sku,"tier":"Fabric"}}
        response = requests.patch(url, headers={'Content-Type': 'application/json', "Authorization": f"Bearer {token}"}, json=payload)
        response.raise_for_status()


