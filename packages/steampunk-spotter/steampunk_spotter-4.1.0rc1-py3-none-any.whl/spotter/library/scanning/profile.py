"""Provide scan profile model."""

import sys
from enum import Enum


class Profile(Enum):
    """Enum that holds profiles with different checks for scanning."""

    DEFAULT = 0
    FULL = 1
    SECURITY = 2

    def __str__(self) -> str:
        """
        Convert Profile to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, profile: str) -> "Profile":
        """
        Convert string profile to Profile object.

        :param profile: Profile for scanning
        :return: Profile object
        """
        try:
            return cls[profile.upper()]
        except KeyError:
            print(
                f"Error: nonexistent profile: {profile}, " f"valid values are: {list(str(e) for e in Profile)}.",
                file=sys.stderr,
            )
            sys.exit(2)
