from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
# import requests
# import urllib.parse
# import json
# import requests
# from lxml import html


class Account:

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

    def get_listing(self, listing_id=0):

        client = OAuth2Session(self.client_id, token=self.token)
        r = client.get(
            "https://backpack.tf/api/1.0/classifieds/listings/" + str(listing_id)
        )

        return r.text

    # alias for compatibility with older versions
    # please use the new name, "get_listing"
    getListing = get_listing
