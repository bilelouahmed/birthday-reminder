import requests
import json
import time
from PIL import Image
from io import BytesIO
from utils import *

DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class Whatsapp:
    def __init__(
        self,
        url: str = "http://localhost:3000",
        webhook_url: str = "http://192.168.1.41:5080",
    ):
        self.url = url
        self.webhook_url = webhook_url

        print("Starting session...")
        starting_session = requests.post(
            url=f"{self.url}/api/sessions/start",
            headers=DEFAULT_HEADERS,
            data=json.dumps(
                {
                    "name": "default",
                    "config": {
                        "proxy": None,
                        "webhooks": [
                            {
                                "url": self.webhook_url,
                                "events": ["message"],
                                "hmac": None,
                                "retries": 5,
                                "customHeaders": None,
                            }
                        ],
                        "debug": None,
                    },
                }
            ),
        )
        if starting_session.status_code == 201:
            time.sleep(10)
            qr_code = requests.get(
                url=f"{self.url}/api/default/auth/qr?format=image",
                headers={"Accept": "image/png"},
            )
            if qr_code.status_code == 200:
                image_bytes = BytesIO(qr_code.content)
                image = Image.open(image_bytes)
                image.show()
                input("Please, scan QR code to continue... Then, press Enter.")
            else:
                print(starting_session.content)
                raise Exception(
                    "Request failed with code status :", qr_code.status_code
                )
        else:
            print(starting_session.content)
            raise Exception(
                f"Something happened while trying to start a Whatsapp session... Please, retry. (code status : {starting_session.status_code})"
            )

    def send_message(self, id: str, message: str):
        chat_id = f"{id}@g.us" if "-" in id else f"{id}@c.us"
        sending_message = requests.post(
            url=f"{self.url}/api/sendText",
            headers=DEFAULT_HEADERS,
            data=json.dumps(
                {
                    "chatId": chat_id,
                    "text": message,
                    "session": "default",
                }
            ),
        )
        if sending_message.status_code != 201:
            print(sending_message.content)
            raise Exception(
                f"Something happened while trying to send a message to {id} (status code : {sending_message.status_code})."
            )

    def get_message_properties(self, data: dict):
        if data["event"] == "message":
            sender_number = data["payload"]["from"].split("@")[0]
            sender = data["payload"].get("notifyName", "")
            received_timestamp = timestamp_to_date(data["payload"]["timestamp"])
            message_received = data["payload"]["body"]
            print(
                f"A new message has been received on {received_timestamp} from {sender_number} ({sender}) : {message_received}."
            )
            return sender_number, sender, received_timestamp, message_received

    # to do : Add history
