class CalendarAppException(Exception):
    """Base exception for all domain-specific errors."""
    pass

class ParticipantNotFoundError(CalendarAppException):
    """Raised when a requested participant is not found in the repository."""
    pass

class InvalidTimeIntervalError(CalendarAppException):
    """Raised when start_time is greater than or equal to end_time."""
    pass

class RepositoryAccessError(CalendarAppException):
    """Raised when the CSV repository fails to read or parse data."""
    pass