from unittest import TestCase

from parknyc.exceptions import InvalidCredentialsError
from parknyc.service import NYCParkingService


class ServiceTestCase(TestCase):
    def test_invalid_credentials(self):
        self.assertRaises(InvalidCredentialsError, NYCParkingService, 'illegal', 'illegal')
