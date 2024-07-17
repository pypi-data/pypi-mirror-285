import json
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class POST:
    def __init__(self, client_id, client_secret, api_key):
        # Self Things
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret

        # Gets The Token
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url="https://backpack.tf/oauth/access_token",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self.token = token

        self.standard_params = {"appid": "440", "key": self.api_key}

    def create_listing(
        self,
        intent=0,
        uid=0,
        quality=6,
        item_name="",
        craftable=1,
        priceindex=0,
        offers=0,
        buyout=1,
        promoted=0,
        details="",
        currencies={"metal": 0},
        account_token="",
    ):
        if intent == 0:
            payload = {
                "token": account_token,
                "listings": [
                    {
                        "intent": str(intent),
                        "item": {
                            "quality": str(quality),
                            "item_name": item_name,
                            "craftable": str(craftable),
                            "priceindex": str(priceindex),
                        },
                        "offers": str(offers),
                        "buyout": str(buyout),
                        "promoted": str(promoted),
                        "details": str(details),
                        "currencies": currencies,
                    }
                ],
            }
        else:
            payload = {
                "token": account_token,
                "listings": [
                    {
                        "id": str(uid),
                        "intent": str(intent),
                        "offers": str(offers),
                        "buyout": str(buyout),
                        "promoted": str(promoted),
                        "details": str(details),
                        "currencies": currencies,
                    }
                ],
            }

        r = requests.post("https://backpack.tf/api/classifieds/list/v1", json=payload)

        jsonResponse = json.loads(r.text)

        try:
            return int(jsonResponse["listings"][item_name]["created"])
        except ValueError:
            return jsonResponse

    createListing = create_listing
