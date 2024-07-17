"""Provide output format model."""

import sys
from enum import Enum


class OutputFormat(Enum):
    """Enum that holds different output formats for scan result."""

    TEXT = 1
    JSON = 2
    YAML = 3

    def __str__(self) -> str:
        """
        Convert OutputFormat to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, output_format: str) -> "OutputFormat":
        """
        Convert string level to OutputFormat object.

        :param output_format: Scan result output format
        :return: OutputFormat object
        """
        try:
            return cls[output_format.upper()]
        except KeyError:
            print(
                f"Error: nonexistent output format: {output_format}, "
                f"valid values are: {list(str(e) for e in OutputFormat)}.",
                file=sys.stderr,
            )
            sys.exit(2)
