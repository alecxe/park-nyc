class NYCParkingError(Exception):
    pass


class InvalidCredentialsError(NYCParkingError):
    pass


class NoDataFoundError(NYCParkingError):
    pass
