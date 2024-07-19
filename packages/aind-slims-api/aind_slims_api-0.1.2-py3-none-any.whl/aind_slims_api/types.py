"""Common types for the SLIMS API.
"""

from typing import Literal

# List of slims tables manually accessed, there are many more
SLIMS_TABLES = Literal[
    "Attachment",
    "Project",
    "Content",
    "ContentEvent",
    "Unit",
    "Result",
    "Test",
    "User",
    "Groups",
    "Instrument",
    "Unit",
]
