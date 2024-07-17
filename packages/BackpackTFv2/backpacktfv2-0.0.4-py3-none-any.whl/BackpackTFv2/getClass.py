# The API is based on the library https://github.com/davidteather/BackpackTf-API/
# Documentation for the backpack.tf API https://backpack.tf/api/index.html#/
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests
import json
import urllib.parse


class GET:
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

    def get_currencies(self):
        currencies = requests.get(
            "https://backpack.tf/api/IGetCurrencies/v1?key=" + self.api_key
        )
        currencyJSON = json.loads(currencies.text)
        if (
                currencyJSON["response"]["success"] == "1"
                or currencyJSON["response"]["success"] == 1
        ):
            return currencyJSON["response"]["currencies"]
        else:
            raise Exception("Your API key is invalid")

    getCurrencies = get_currencies

    def get_pricehistory(self, **kwargs):
        kwargs.update(self.standard_params)
        encoded = urllib.parse.urlencode(kwargs)
        r = requests.get("https://backpack.tf/api/IGetPriceHistory/v1?" + encoded)
        jsondata = json.loads(r.text)

        success = False
        try:
            if (
                    jsondata["response"]["success"] == 1
                    or jsondata["response"]["success"] == "1"
            ):
                success = True
        except ValueError:
            return jsondata

        if success:
            return jsondata["response"]["history"][
                len(jsondata["response"]["history"]) - 1
                ]
        else:
            raise Exception("Request Unsuccessful.")

    getPiceHistory = get_pricehistory

    def get_prices(self, raw=2, since=0):

        r = requests.get(
            "https://backpack.tf/api/IGetPrices/v4?raw="
            + str(raw)
            + "&since="
            + str(since)
            + "&key="
            + self.api_key
        )
        jsondata = json.loads(r.text)

        success = False
        try:
            if (
                    jsondata["response"]["success"] == 1
                    or jsondata["response"]["success"] == "1"
            ):
                success = True
        except ValueError:
            return jsondata

        if success:
            return jsondata["response"]
        else:
            raise Exception("Unsuccessful Request")

    getPrices = get_prices

    def get_listing(self, listing_id=0):

        client = OAuth2Session(self.client_id, token=self.token)
        r = client.get(
            "https://backpack.tf/api/1.0/classifieds/listings/" + str(listing_id)
        )

        return r.text

    # alias for compatibility with older versions
    # please use the new name, "get_listing"
    getListing = get_listing
