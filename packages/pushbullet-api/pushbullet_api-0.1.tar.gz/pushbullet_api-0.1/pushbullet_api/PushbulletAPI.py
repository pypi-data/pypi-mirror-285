import requests
import json

class PushbulletAPI:
    BASE_URL = "https://api.pushbullet.com/v2"

    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            'Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }

    def _post(self, endpoint, data):
        response = requests.post(
            f"{self.BASE_URL}/{endpoint}",
            headers=self.headers,
            data=json.dumps(data)
        )
        return response.json()

    def _delete(self, endpoint):
        response = requests.delete(
            f"{self.BASE_URL}/{endpoint}",
            headers=self.headers
        )
        return response.json()

    # Text Messaging
    def create_text(self, target_device_iden, addresses, message, guid, file_url=None, file_type=None, skip_delete_file=True):
        data = {
            "data": {
                "addresses": addresses,
                "message": message,
                "target_device_iden": target_device_iden,
                "guid": guid
            },
            "skip_delete_file": skip_delete_file
        }
        
        if file_url:
            data["file_url"] = file_url
        if file_type:
            data["data"]["file_type"] = file_type
        
        return self._post("texts", data)

    def update_text(self, iden, addresses, message, guid, file_url=None, file_type=None, skip_delete_file=True):
        data = {
            "data": {
                "addresses": addresses,
                "message": message,
                "guid": guid
            },
            "skip_delete_file": skip_delete_file,
            "iden": iden
        }

        if file_url:
            data["file_url"] = file_url
        if file_type:
            data["data"]["file_type"] = file_type
        
        return self._post(f"texts/{iden}", data)

    def delete_text(self, iden):
        return self._delete(f"texts/{iden}")

    # Universal Pushbullet Operations
    def push_note(self, device_iden, title, body):
        data = {
            "type": "note",
            "title": title,
            "body": body,
            "device_iden": device_iden
        }
        return self._post("pushes", data)

    def push_link(self, device_iden, title, url, body=None):
        data = {
            "type": "link",
            "title": title,
            "url": url,
            "device_iden": device_iden
        }
        if body:
            data["body"] = body
        return self._post("pushes", data)

    def push_file(self, device_iden, file_name, file_type, file_url, body=None):
        data = {
            "type": "file",
            "file_name": file_name,
            "file_type": file_type,
            "file_url": file_url,
            "device_iden": device_iden
        }
        if body:
            data["body"] = body
        return self._post("pushes", data)
