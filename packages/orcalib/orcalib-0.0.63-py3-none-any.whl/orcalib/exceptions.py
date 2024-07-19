class OrcaException(Exception):
    """Base exception type for OrcaLib"""

    def __init__(self, message, content=None):
        """
        Initialize the exception.

        Args:
            message: The error message
            content: The http content of the request if available
        """
        self.content = content
        super(OrcaException, self).__init__(message)


class OrcaNotFoundException(OrcaException):
    """Exception raised when a resource is not found."""

    pass


class OrcaUnauthenticatedException(OrcaException):
    """Exception raised when a request is made without an authentication token."""

    pass


class OrcaUnauthorizedException(OrcaException):
    """Exception raised when a request is made without the proper permissions."""

    pass


class OrcaBadRequestException(OrcaException):
    """Exception raised when a request is made with invalid parameters."""

    pass
