class NYCParkingError(Exception):
    pass


class InvalidCredentialsError(NYCParkingError):
    pass


class NoDataFoundError(NYCParkingError):
    pass


class NoParkingZoneError(NYCParkingError):
    pass


class InvalidParkingSessionDuration(NYCParkingError):
    pass


class VerificationFailedError(NYCParkingError):
    pass


class CannotStartParkingSessionError(NYCParkingError):
    pass
