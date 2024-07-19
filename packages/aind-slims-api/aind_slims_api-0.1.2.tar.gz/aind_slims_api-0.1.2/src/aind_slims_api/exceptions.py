"""Custom exceptions for the AIND Slims API."""


class SlimsAPIException(Exception):
    """Base exception for the AIND Slims API."""


class SlimsRecordNotFound(SlimsAPIException):
    """Exception raised when a record is not found in the SLIMS database."""
