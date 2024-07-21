import requests as WEB

class Webhook():
    """
    Contains the information to access a Discord webhook

    #### Arguments:
        url (str): The webhook url to send messages through 

    #### Methods:
        send(): Sends a message through the webhook
    """
    def __init__(self, url: str):
        self._url = url

    def send(self, msg: str):
        """
        Sends a message through the webhook

        #### Arguments
            msg (str): 

        #### Raises:
        requests.exceptions.HTTPError: If the message couldn't be sent
        """
        payload = {"content": msg}
        response = WEB.post(self._url, json=payload)
        
        response.raise_for_status()
