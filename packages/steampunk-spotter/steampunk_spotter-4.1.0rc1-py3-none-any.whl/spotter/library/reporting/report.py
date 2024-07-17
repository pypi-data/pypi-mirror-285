"""This is an interface for generating modular reports in various formats."""

import itertools
import json
import sys
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Union
from pydantic_core import to_jsonable_python

from spotter.library.reporting.sarif.models import (
    SarifFile,
    Result,
    Run,
    Tool,
    ToolDriver,
    DriverRules,
    DriverRulesShortDescription,
    Message,
    Location,
    PhysicalLocation,
    ArtifactLocation,
    Region,
    DriverRulesHelp,
)
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.utils import get_current_cli_version

if TYPE_CHECKING:
    # cylic import
    from spotter.library.scanning.check_result import CheckResult


class ReportingInterface(ABC):
    """Interface for generating modular reports in various formats."""

    @abstractmethod
    def render(self, check_results: List["CheckResult"], disable_docs_url: bool) -> str:
        """
        Render the report based on the provided args as a string in the appropriate format.

        :param check_results: Root node
        :param disable_docs_url: Disable outputting URL to documentation
        :return: Report
        """


class JUnitXml(ReportingInterface):
    """Generate JUnit XML file."""

    def add_root_node(self) -> ET.Element:
        """Add root node to the XML report."""
        root = ET.Element("testsuites")
        return root

    def add_test_suite(self, root_node: ET.Element, name: str) -> ET.Element:
        """
        Add test suite to the XML report.

        :param root_node: Root node
        :param name: Test suite name
        :return: ET.Element object
        """
        test_suite = ET.SubElement(root_node, "testsuite", name=name)
        return test_suite

    def add_test_case(self, test_suite: ET.Element, name: str, classname: str) -> ET.Element:
        """
        Add test case to the XML report.

        :param test_suite: Test suite
        :param name: Test case name
        :param classname: Test case classname
        :return: ET.Element object
        """
        test_case = ET.SubElement(test_suite, "testcase", name=name, classname=classname)
        return test_case

    def add_failure_info(self, test_case: ET.Element, message: str, typ: str) -> ET.Element:
        """
        Add failure info to the XML report.

        :param test_case: Test case
        :param message: Error message
        :param typ: Error type
        :return: ET.Element object
        """
        error_case = ET.SubElement(test_case, "error", message=message, type=typ)
        return error_case

    def add_attribute(self, element: ET.Element, key: str, value: str) -> None:
        """
        Add attribute to the XML report.

        :param element: ET.Element object
        :param key: Attribute key
        :param value: Attribute value
        """
        element.set(key, value)

    def render(self, check_results: List["CheckResult"], disable_docs_url: bool = False) -> str:
        """
        Render the report.

        :param check_results: List of check results
        :param disable_docs_url: Disable outputting URL to documentation
        :return: Junit XML report
        """
        root_node = self.add_root_node()
        get_check_class = lambda res: res.catalog_info.check_class  # pylint: disable=unnecessary-lambda-assignment
        for c_class, c_results in itertools.groupby(sorted(check_results, key=get_check_class), get_check_class):
            test_suite = self.add_test_suite(root_node, c_class)
            check_count = 0

            for result in c_results:
                test_case = self.add_test_case(
                    test_suite,
                    f"{result.catalog_info.event_code}-{result.catalog_info.event_value}[{check_count}]",
                    c_class,
                )
                self.add_attribute(test_case, "id", str(result.catalog_info.event_code))
                self.add_attribute(test_case, "file", str(result.metadata.file_name if result.metadata else ""))
                self.add_failure_info(
                    test_case,
                    result.construct_output(True, disable_docs_url, True),
                    result.level.name.upper(),
                )

                check_count += 1

            self.add_attribute(test_suite, "tests", str(check_count))
            self.add_attribute(test_suite, "errors", str(check_count))

        if sys.version_info >= (3, 9):
            # ET.indent works only for Python >= 3.9
            ET.indent(root_node)

        return ET.tostring(root_node, encoding="unicode", method="xml")


class SarifReport(ReportingInterface):
    """Generate SARIF file."""

    TOOL_NAME = "Steampunk Spotter"
    CATALOG_URL = "https://spotter.steampunk.si/check-catalogue/"
    INFORMATION_URI = "https://steampunk.si/spotter/"

    def _convert_level_error(self, spotter_error_lvl: DisplayLevel) -> str:
        """
        Convert the error level from the spotter to a standardized format.

        :param spotter_error_lvl: The error level from the spotter.
        :return: The standardized error level.
        """
        lvl = spotter_error_lvl.name.lower()
        if lvl == "hint":
            return "note"
        return lvl

    def _create_driver_rule(self, check_result: "CheckResult", disable_docs_url: bool) -> DriverRules:
        """
        Create a driver rule object based on the provided check result.

        :param check_result: The check result object.
        :return: The driver rule generated.
        """
        driver_help = DriverRulesHelp(text="")
        if not disable_docs_url and check_result.doc_url is not None:
            driver_help.text = check_result.doc_url
        return DriverRules(
            id=check_result.catalog_info.event_code,
            name=check_result.catalog_info.event_value,
            shortDescription=DriverRulesShortDescription(text=check_result.catalog_info.event_value),
            help=driver_help,
        )

    def _create_results(self, check_result: "CheckResult", location: Union[Location, None]) -> Result:
        """
        Create results object based on the provided check result and location.

        :param check_result: The check result object.
        :param location: The location of the check result, if available.
        :return: The generated result.
        """
        return Result(
            ruleId=check_result.catalog_info.event_code,
            level=self._convert_level_error(check_result.level),
            message=Message(text=check_result.message),
            locations=[location],
        )

    def _create_location(self, check_result: "CheckResult") -> Union[Location, None]:
        """
        Create a location object based on the provided check result.

        :param check_result: The check result object.
        :return: The generated location, or None if metadata is not available.
        """
        if check_result.metadata:
            uri = check_result.metadata.file_name
            if uri.startswith("/"):  # sarif does not support leading slash in uri
                uri = uri[1:]

            return Location(
                physicalLocation=PhysicalLocation(
                    artifactLocation=ArtifactLocation(uri=uri),
                    region=Region(startLine=check_result.metadata.line, startColumn=check_result.metadata.column),
                )
            )
        return None

    def _create_tool(self, driver_rules: List[DriverRules]) -> Tool:
        """
        Create a tool object based on the provided driver rules.

        :param driver_rules: The list of driver rules.
        :return: The generated tool.
        """
        return Tool(
            driver=ToolDriver(
                name=self.TOOL_NAME,
                version=get_current_cli_version(),
                informationUri=self.INFORMATION_URI,
                rules=driver_rules,
            )
        )

    def render(self, check_results: List["CheckResult"], disable_docs_url: bool = False) -> str:
        """
        Render the SARIF (Static Analysis Results Interchange Format) report.

        :param check_results: A list of CheckResult objects.
        :param disable_docs_url: Disable outputting URL to documentation
        :return: The SARIF report in JSON format.
        """
        if len(check_results) == 0:
            return json.dumps(to_jsonable_python(SarifFile(), by_alias=True), indent=4)

        driver_rules = []
        results = []
        for cr in check_results:
            location = self._create_location(cr)
            driver_rule = self._create_driver_rule(cr, disable_docs_url)
            if driver_rule not in driver_rules:
                driver_rules.append(driver_rule)
            result = self._create_results(cr, location)
            if result not in results:
                results.append(result)
        tool = self._create_tool(driver_rules)
        return json.dumps(
            to_jsonable_python(SarifFile(runs=[Run(tool=tool, results=results)]), by_alias=True), indent=4
        )
