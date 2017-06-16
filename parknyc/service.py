from base64 import b64encode

from parknyc.exceptions import NoDataFoundError, InvalidCredentialsError

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests


API_BASE_URL = "https://parknyc.parkmobile.us/phonixxapi/"
API_BASE_PAYLOAD = {"appId": "PhonixxWeb", "appVersion": "1", "scope": "Api"}


class NYCParkingService:
    """NYC Parking service wrapper class."""

    def __init__(self, username, password):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "SourceAppKey": "NycMobile",
        }
        self.session.get("https://parknyc.parkmobile.us/parknyc/app/#/login")  # visit main page

        auth_header = b64encode("{username}:{password}".format(username=username, password=password).encode("utf-8")).decode('utf-8')
        self.__login(auth_header)
        self.__get_identity()

    def __login(self, auth_header):
        # get the authentication token
        response = self.session.post(urljoin(API_BASE_URL, "Token2?format=json"),
                                     json=API_BASE_PAYLOAD,
                                     headers={"Authorization": "Basic {auth_header}".format(auth_header=auth_header)})
        if response.status_code == 400:
            raise InvalidCredentialsError("Invalid credentials")

        data = response.json()
        self.session.headers.update({"PMAuthenticationToken": data['token']})

    def __get_identity(self):
        """Gets the service identity information"""
        response = self.session.get(urljoin(API_BASE_URL, "account/identify2"))
        return response.json()

    def history_sessions(self):
        """Generates history parking session data."""
        response = self.session.get(urljoin(API_BASE_URL, "parking/history"))

        if response.status_code == 404:
            raise NoDataFoundError("No historical parking sessions found")

        yield response.json()

    def active_sessions(self):
        """Generates active parking session data."""
        response = self.session.get(urljoin(API_BASE_URL, "parking/active"))

        if response.status_code == 404:
            raise NoDataFoundError("No active parking sessions found")

        yield response.json()
