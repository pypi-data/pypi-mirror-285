from typing import Optional, List

from pydantic import BaseModel, Field


class ArtifactLocation(BaseModel):
    """Represents a ArtifactLocation in a SARIF file."""

    uri: str


class Region(BaseModel):
    """Represents a region in a SARIF file."""

    startLine: int
    startColumn: int


class PhysicalLocation(BaseModel):
    """Represents a physical location in a SARIF file."""

    artifactLocation: ArtifactLocation
    region: Region


class Message(BaseModel):
    """Represents a message in a SARIF result."""

    text: str


class Location(BaseModel):
    """Represents a location in a SARIF result."""

    physicalLocation: Optional[PhysicalLocation] = None


class Result(BaseModel):
    """Represents a result in a SARIF run."""

    ruleId: str
    level: str
    message: Message
    locations: List[Location]


class DriverRulesHelp(BaseModel):
    """Represents a help object in a Sarif drive rules."""

    text: str


class DriverRulesShortDescription(BaseModel):
    """Represents a short description in a Sarif drive rules."""

    text: str


class DriverRules(BaseModel):
    """Represents a driver rules in a Sarif tool driver."""

    id: str
    name: str
    shortDescription: DriverRulesShortDescription
    help: DriverRulesHelp


class ToolDriver(BaseModel):
    """Represents a tool driver in a SARIF tool."""

    name: str
    version: str
    informationUri: str
    rules: List[DriverRules]


class Tool(BaseModel):
    """Represents a tool in a SARIF run."""

    driver: Optional[ToolDriver]


class Run(BaseModel):
    """Represents a run in a SARIF file."""

    tool: Optional[Tool] = None
    results: Optional[List[Result]] = []


class SarifFile(BaseModel):
    """Represents a SARIF file."""

    schema_url: str = Field(
        default="https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        alias="$schema",
    )
    version: str = "2.1.0"
    runs: Optional[List[Run]] = []
