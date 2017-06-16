from base64 import b64encode
from datetime import datetime, timedelta
import uuid

from parknyc.exceptions import *  # noqa

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
        """Gets the service identity information."""
        response = self.session.get(urljoin(API_BASE_URL, "account/identify2"))
        return response.json()

    def history_sessions(self):
        """Generates history parking session data."""
        response = self.session.get(urljoin(API_BASE_URL, "parking/history"))

        if response.status_code == 404:
            raise NoDataFoundError("No historical parking sessions found")

        for session in response.json()['actions']:
            yield session

    def active_sessions(self):
        """Generates active parking session data."""
        response = self.session.get(urljoin(API_BASE_URL, "parking/active"))

        if response.status_code == 404:
            raise NoDataFoundError("No active parking sessions found")

        for session in response.json()['actions']:
            yield session

    def start_session(self, zone, duration):
        """
        Starts parking at the given zone for a given amount of time.

        :param zone: zone number as an integer or a string
        :param duration: parking duration as an int - number of minutes
        """
        response = self.session.get(urljoin(API_BASE_URL, "parking/zones/{zone}".format(zone=zone)))

        if response.status_code == 404:
            raise NoParkingZoneError("Zone '{zone}' is not a valid parking zone")

        # check that the given duration is supported for this zone
        zone_data = response.json()['zones'][0]
        available_durations = [
            selection['hour'] * 60 + minute_selection
            for selection in zone_data['parkInfo']['durationSelections']['hourMinuteDurationSelections']
            for minute_selection in selection['minutes']
        ]
        if duration not in available_durations:
            raise InvalidParkingSessionDuration(
                "Duration {duration} is not valid. Available options are: {available_durations}".format(duration=duration,
                                                                                                        available_durations=", ".join(available_durations)))

        # get the first vehicle TODO: it should be given as an input as well
        response = self.session.get(urljoin(API_BASE_URL, "account/vehicles"))

        if response.status_code == 404:
            raise NoDataFoundError("No configured vehicles found in the account")

        vehicle_data = response.json()['vehicles'][0]

        self.__park(zone_data, vehicle_data, duration)

    def __park(self, zone_data, vehicle_data, duration):
        """
        Parks the car taking into account the zone, vehicle data and duration.
        Returns parking ID of the new session.
        """

        # generate temporary token
        token = str(uuid.uuid1()).replace("-", "")

        # post verification token - only 404 would mean we can proceed
        response = self.session.post(urljoin(API_BASE_URL, "parking/verification"), data={"token": token})
        if response.status_code != 404:
            raise VerificationFailedError("Could not verify parking information")

        # prepare the payload
        now = datetime.utcnow()
        start_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (now + timedelta(minutes=duration)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            "id": 0,
            "internalZoneCode": zone_data['internalZoneCode'],
            "spaceNumber": "",
            "pushToken": "",
            "device": "",
            "SourceAppKey": "NycMobile",
            "vehicleId": vehicle_data['vehicleId'],
            "vehicleVrn": vehicle_data['vrn'],
            "vehicleVrnState": vehicle_data['state'],
            "durationInMinutes": duration,
            "verification": {"isExtention": False,
                             "lpn": "",
                             "parkingActionId": 0,
                             "token": token,
                             "zoneCode": zone_data['signageCode']},
            "selectedBillingMethodId": None,
            "selectedDiscounts": "{NONE}",
            "startTimeLocal": start_time,
            "stopTimeLocal": end_time,
            "vehicleVin": "",
            "masterPassTransaction": False,
            "lon": "",
            "lat": ""
        }
        response = self.session.post(urljoin(API_BASE_URL, "parking/active"), json=data)

        if response.status_code != 201:
            raise CannotStartParkingSessionError("Cannot start new parking session")

        return response.json()['parkingActionId']
