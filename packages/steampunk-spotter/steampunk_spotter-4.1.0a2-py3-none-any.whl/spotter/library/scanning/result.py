"""Provide scan result model."""
import json
import sys
import xml
from io import StringIO
from typing import List, Dict, Any, Optional, Tuple, cast

from pathlib import Path
import ruamel.yaml as ruamel
from colorama import Fore, Style
from pydantic import BaseModel

from spotter.library.scanning.parser_error import YamlErrorDetails
from spotter.library.reporting.report import JUnitXml, SarifReport
from spotter.library.rewriting.models import RewriteSuggestion, CheckType
from spotter.library.rewriting.processor import update_files
from spotter.library.scanning.check_catalog_info import CheckCatalogInfo
from spotter.library.scanning.check_result import CheckResult
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.item_metadata import ItemMetadata
from spotter.library.scanning.output_format import OutputFormat
from spotter.library.scanning.progress import Progress
from spotter.library.scanning.summary import Summary


class Result(BaseModel):
    """A container for scan result originating from the backend."""

    # TODO: Add more fields from scan response if we need them
    # pylint: disable=too-many-instance-attributes
    uuid: Optional[str] = None
    user: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None
    project: Optional[str] = None
    organization: Optional[str] = None
    environment: Optional[Dict[str, Any]] = None
    scan_date: Optional[str] = None
    subscription: Optional[str] = None
    is_paid: Optional[bool] = None
    web_urls: Optional[Dict[str, str]] = None
    summary: Summary
    scan_progress: Progress
    check_results: List[CheckResult]
    fixed_check_results: List[CheckResult]

    @classmethod
    def from_api_response(
        cls,
        response_json: Dict[str, Any],
        input_tasks: List[Dict[str, Any]],
        input_playbooks: List[Dict[str, Any]],
        input_inventories: List[Dict[str, Any]],
        scan_time: float,
    ) -> "Result":
        """
        Convert scan API response to Result object.

        :param response_json: The backend API response in JSON format
        :param input_tasks: The scanned tasks with no information removed
        :param input_playbooks: The scanned playbooks with plays that have no information removed
        :param scan_time: Time taken to do a scan
        :return: Result object
        """
        scan_result = cls(
            uuid=response_json.get("id", ""),
            user=response_json.get("user", ""),
            user_info=response_json.get("user_info", {}),
            project=response_json.get("project", ""),
            organization=response_json.get("organization", ""),
            environment=response_json.get("environment", {}),
            scan_date=response_json.get("scan_date", ""),
            subscription=response_json.get("subscription", ""),
            is_paid=response_json.get("is_paid", False),
            web_urls=response_json.get("web_urls", {}),
            summary=Summary(
                scan_time=scan_time, num_errors=0, num_warnings=0, num_hints=0, status=response_json.get("status", "")
            ),
            scan_progress=Progress.from_api_response_element(response_json.get("scan_progress", {})),
            check_results=[],
            fixed_check_results=[],
        )
        scan_result.parse_check_results(response_json, input_tasks, input_playbooks, input_inventories)
        return scan_result

    @staticmethod
    def _parse_known_check_result(
        element: Dict[str, Any], input_items: Dict[str, Dict[str, Any]]
    ) -> Optional[CheckResult]:
        check_type: CheckType = CheckType.from_string(element.get("check_type", ""))
        good_check_types = [CheckType.TASK, CheckType.PLAY, CheckType.INVENTORY]
        if check_type not in good_check_types:
            print(
                f"Error: incorrect check type '{check_type}'. Should be one of {good_check_types}.",
                file=sys.stderr,
            )
            sys.exit(2)

        correlation_id = element.get("correlation_id")
        if not correlation_id:
            print(
                "Error: correlation id for result was not set. This should not happen for a task or play.",
                file=sys.stderr,
            )
            sys.exit(2)

        # guard against incomplete results where we don't match a task or play
        original_item = input_items.get(correlation_id)
        if not original_item:
            print("Could not map task ID to its original task.")
            return None

        # guard against missing task or play args and metadata
        item_meta = original_item.get("spotter_metadata", None)
        if not item_meta:
            print("Meta data is missing.")
            return None

        suggestion = element.get("suggestion", "")
        item_metadata_object = ItemMetadata.from_item_meta(item_meta)
        display_level = DisplayLevel.from_string(element.get("level", ""))

        suggestion_object: Optional[RewriteSuggestion] = RewriteSuggestion.from_item(
            check_type, original_item, suggestion, display_level
        )

        result = CheckResult(
            correlation_id=correlation_id,
            original_item=original_item,
            metadata=item_metadata_object,
            catalog_info=CheckCatalogInfo.from_api_response_element(element),
            level=display_level,
            message=element.get("message", ""),
            suggestion=suggestion_object,
            doc_url=element.get("doc_url", ""),
            check_type=check_type,
        )
        return result

    @staticmethod
    def _parse_unknown_check_result(element: Dict[str, Any]) -> CheckResult:
        check_type = CheckType.from_string(element.get("check_type", ""))
        display_level = DisplayLevel.from_string(element.get("level", ""))
        check_catalog_info = CheckCatalogInfo.from_api_response_element(element)

        result = CheckResult(
            correlation_id="",
            original_item={},
            metadata=None,
            catalog_info=check_catalog_info,
            level=display_level,
            message=element.get("message", ""),
            suggestion=None,
            doc_url=element.get("doc_url", ""),
            check_type=check_type,
        )
        return result

    def parse_check_results(
        self,
        response_json: Dict[str, Any],
        input_tasks: List[Dict[str, Any]],
        input_playbooks: List[Dict[str, Any]],
        input_inventories: List[Dict[str, Any]],
    ) -> None:
        """
        Parse result objects and map tasks with complete information.

        :param response_json: The backend API response in JSON format
        :param input_tasks: The scanned tasks with no information removed
        :param input_playbooks: The scanned playbooks with plays that have no information removed
        """
        tasks_as_dict = {x["task_id"]: x for x in input_tasks if "task_id" in x}
        plays_as_dict = {}
        inventories_as_dict = {x["dynamic_inventory_id"]: x for x in input_inventories if "dynamic_inventory_id" in x}
        for playbook in input_playbooks:
            plays_as_dict.update({x["play_id"]: x for x in playbook["plays"] if "play_id" in x})

        result: List[CheckResult] = []
        for element in response_json.get("elements", []):
            check_type = CheckType.from_string(element.get("check_type", ""))
            item: Optional[CheckResult] = None

            if check_type == CheckType.TASK:
                item = self._parse_known_check_result(element, tasks_as_dict)
            elif check_type == CheckType.PLAY:
                item = self._parse_known_check_result(element, plays_as_dict)
            elif check_type == CheckType.INVENTORY:
                item = self._parse_known_check_result(element, inventories_as_dict)
            else:
                item = self._parse_unknown_check_result(element)

            if item:
                self.summary.update(item)
                result.append(item)
        self.check_results = result

    def filter_check_results(self, threshold: DisplayLevel) -> None:
        """
        Filter a list of check results by only keeping tasks over a specified severity level.

        :param threshold: The DisplayLevel object as threshold (inclusive) of what level messages (and above) to keep
        """
        self.check_results = [cr for cr in self.check_results if cr.level.value >= threshold.value]

    @staticmethod
    def _get_sort_key(check_result: CheckResult) -> Tuple[str, int, int, int]:
        """
        Extract a tuple of file name, line number, column number and negative display level from check result.

        This is a key function for sorting check results.

        :param check_result: CheckResult object
        :return: A tuple of file name, line number, column number, and negative display level
        """
        if not check_result.metadata:
            return "", 0, 0, 0
        return (
            check_result.metadata.file_name,
            int(check_result.metadata.line),
            int(check_result.metadata.column),
            -check_result.level.value,
        )

    def sort_check_results(self) -> None:
        """Sort a list of check results by file names (alphabetically) and also YAML line and column numbers."""
        self.check_results.sort(key=self._get_sort_key)

    # TODO: Refactor this function to multiple smaller functions
    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
    def _format_text(
        self,
        errors: Optional[List[YamlErrorDetails]] = None,
        disable_colors: bool = False,
        disable_docs_url: bool = False,
        disable_scan_url: bool = False,
        rewrite: bool = False,
    ) -> str:
        """
        Format scan result as text.

        :param disable_colors: Disable output colors and styling
        :param disable_docs_url: Disable outputting URL to documentation
        :param disable_scan_url: Disable outputting URL to scan result
        :param rewrite: Rewrite files with fixes
        :return: A formatted string
        """
        output = ""

        parsing_error_label = ""
        parsing_errors = ""
        if errors:
            parsing_error_label = "YAML parsing errors"
            parsing_error_specific = []
            for error in errors:
                parsing_error_specific.append(f"{error.file_path}:{error.line}:{error.column}: {error.description}")
            parsing_errors = "\n".join(parsing_error_specific)

        fixed_check_results_label = ""
        fixed_check_results = ""
        if self.fixed_check_results:
            fixed_check_results_label = "Rewritten check results"
            for result_fixed in self.fixed_check_results:
                fixed_check_results += result_fixed.construct_output(disable_colors, disable_docs_url, True) + "\n"

        check_results_label = ""
        check_results = ""
        if self.check_results:
            if self.fixed_check_results:
                check_results_label = "Remaining check results"
            else:
                check_results_label = "Check results"
        for result in self.check_results:
            check_results += result.construct_output(disable_colors, disable_docs_url) + "\n"

        def level_sort_key(level: DisplayLevel) -> int:
            return cast(int, level.value)

        worst_level = DisplayLevel.SUCCESS
        scan_summary_label = "Scan summary"
        if len(self.check_results) > 0:
            worst_level = max((cr.level for cr in self.check_results), key=level_sort_key)

        if rewrite:
            suggestion_level_file_tuples = [
                (cr.suggestion, cr.metadata.file_name)
                for cr in self.fixed_check_results
                if cr.suggestion is not None and cr.metadata is not None
            ]
        else:
            suggestion_level_file_tuples = [
                (cr.suggestion, cr.metadata.file_name)
                for cr in self.check_results
                if cr.suggestion is not None and cr.metadata is not None
            ]
        rewrite_files_len = len(set(t[1] for t in suggestion_level_file_tuples))
        rewrite_message = (
            f"{'Did' if rewrite else 'Can'} rewrite {rewrite_files_len} file(s) with "
            f"{len(suggestion_level_file_tuples)} change(s)."
        )
        time_message = f"Spotter took {self.summary.scan_time:.3f} s to scan your input."
        stats_message = (
            f"It resulted in {self.summary.num_errors} error(s), {self.summary.num_warnings} "
            f"warning(s) and {self.summary.num_hints} hint(s)."
        )
        overall_status_message = f"Overall status: {worst_level.name.upper()}"

        view_scan_url_message = ""
        scan_url = None
        if not disable_scan_url and self.web_urls:
            scan_url = self.web_urls.get("scan_url", None)
            view_scan_url_message = f"Visit {scan_url} to view this scan result."

        if not disable_colors:
            if parsing_error_label:
                parsing_error_label = f"{Style.BRIGHT}{parsing_error_label}{Style.NORMAL}"
            if fixed_check_results_label:
                fixed_check_results_label = f"{Style.BRIGHT}{fixed_check_results_label}{Style.NORMAL}"
            if check_results_label:
                check_results_label = f"{Style.BRIGHT}{check_results_label}{Style.NORMAL}"
            if scan_summary_label:
                scan_summary_label = f"{Style.BRIGHT}{scan_summary_label}{Style.NORMAL}"
            time_message = (
                f"Spotter took {Style.BRIGHT}{self.summary.scan_time:.3f} s{Style.NORMAL} to scan " f"your input."
            )
            stats_message = (
                f"It resulted in {Style.BRIGHT + Fore.RED}{self.summary.num_errors} error(s)"
                f"{Fore.RESET + Style.NORMAL}, {Style.BRIGHT + Fore.YELLOW}{self.summary.num_warnings} "
                f"warning(s){Fore.RESET + Style.NORMAL} and {Style.BRIGHT}{self.summary.num_hints} "
                f"hint(s){Style.NORMAL}."
            )
            rewrite_message = (
                f"{'Did' if rewrite else 'Can'} {Style.BRIGHT + Fore.MAGENTA}rewrite{Fore.RESET + Style.NORMAL} "
                f"{Style.BRIGHT}{rewrite_files_len} file(s){Style.NORMAL} with "
                f"{Style.BRIGHT}{len(suggestion_level_file_tuples)} change(s){Style.NORMAL}."
            )

            if worst_level == DisplayLevel.ERROR:
                overall_status_message = (
                    f"Overall status: {Style.BRIGHT + Fore.RED}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
                )
            elif worst_level == DisplayLevel.WARNING:
                overall_status_message = (
                    f"Overall status: {Style.BRIGHT + Fore.YELLOW}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
                )
            elif worst_level == DisplayLevel.HINT:
                overall_status_message = f"Overall status: {Style.BRIGHT}{worst_level.name.upper()}{Style.NORMAL}"
            else:
                overall_status_message = (
                    f"Overall status: {Style.BRIGHT + Fore.GREEN}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
                )

            if scan_url:
                view_scan_url_message = f"Visit {Fore.CYAN}{scan_url}{Fore.RESET} to view this scan result."
        if parsing_errors:
            output += f"{parsing_error_label}:\n{parsing_errors}\n\n"
        if self.fixed_check_results and self.check_results:
            output += (
                f"{fixed_check_results_label}:\n{fixed_check_results}\n{check_results_label}:\n"
                f"{check_results}\n{scan_summary_label}:\n{time_message}\n{stats_message}\n"
                f"{rewrite_message}\n{overall_status_message}"
            )
        elif self.fixed_check_results:
            output += (
                f"{fixed_check_results_label}:\n{fixed_check_results}\n{scan_summary_label}:\n{time_message}"
                f"\n{stats_message}\n{rewrite_message}\n{overall_status_message}"
            )
        elif self.check_results:
            output += (
                f"{check_results_label}:\n{check_results}\n{scan_summary_label}:\n{time_message}\n"
                f"{stats_message}\n{rewrite_message}\n{overall_status_message}"
            )
        else:
            output += (
                f"{scan_summary_label}:\n{time_message}\n{stats_message}\n{rewrite_message}\n{overall_status_message}"
            )

        if view_scan_url_message:
            output += f"\n{view_scan_url_message}"

        return output

    def _format_dict(self, disable_docs_url: bool = False, disable_scan_url: bool = False) -> Dict[str, Any]:
        """
        Format scan result as Python dict.

        :param disable_docs_url: Disable outputting URL to documentation
        :param disable_scan_url: Disable outputting URL to scan result
        :return: A formatted string
        """
        check_result_outputs = []
        for result in self.check_results:
            metadata = result.metadata or ItemMetadata(file_name="", line=0, column=0)
            catalog_info = result.catalog_info
            suggestion_dict = {}
            if result.suggestion:
                suggestion_dict = {
                    "start_mark": result.suggestion.start_mark,
                    "end_mark": result.suggestion.end_mark,
                    "suggestion": result.suggestion.suggestion_spec,
                }

            check_result_outputs.append(
                {
                    "task_id": result.correlation_id,  # It is here because we want to be back compatible
                    "file": metadata.file_name,
                    "line": metadata.line,
                    "column": metadata.column,
                    "check_class": catalog_info.check_class,
                    "event_code": catalog_info.event_code,
                    "event_value": catalog_info.event_value,
                    "event_message": catalog_info.event_message,
                    "event_subcode": catalog_info.event_subcode,
                    "event_submessage": catalog_info.event_submessage,
                    "level": result.level.name.strip(),
                    "message": result.message.strip(),
                    "suggestion": suggestion_dict,
                    "doc_url": None if disable_docs_url else result.doc_url,
                    "correlation_id": result.correlation_id,
                    "check_type": result.check_type.name.strip(),
                }
            )

        return {
            "uuid": self.uuid,
            "user": self.user,
            "user_info": self.user_info,
            "project": self.project,
            "organization": self.organization,
            "environment": self.environment,
            "scan_date": self.scan_date,
            "subscription": self.subscription,
            "is_paid": self.is_paid,
            "web_urls": None if disable_scan_url else self.web_urls,
            "summary": {
                "scan_time": self.summary.scan_time,
                "num_errors": self.summary.num_errors,
                "num_warnings": self.summary.num_warnings,
                "num_hints": self.summary.num_hints,
                "status": self.summary.status,
            },
            "scan_progress": {
                "progress_status": str(self.scan_progress.progress_status),
                "current": self.scan_progress.current,
                "total": self.scan_progress.total,
            },
            "check_results": check_result_outputs,
        }

    def _format_json(self, disable_docs_url: bool = False, disable_scan_url: bool = False) -> str:
        """
        Format scan result as JSON.

        :param disable_docs_url: Disable outputting URL to documentation
        :param disable_scan_url: Disable outputting URL to scan result
        :return: A formatted string
        """
        return json.dumps(self._format_dict(disable_docs_url, disable_scan_url), indent=2)

    def _format_yaml(self, disable_docs_url: bool = False, disable_scan_url: bool = False) -> str:
        """
        Format scan result as YAML.

        :param disable_docs_url: Disable outputting URL to documentation
        :param disable_scan_url: Disable outputting URL to scan result
        :return: A formatted string
        """
        stream = StringIO()
        yaml = ruamel.YAML(typ="rt")
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(self._format_dict(disable_docs_url, disable_scan_url), stream=stream)
        return stream.getvalue()

    def format_junit_xml(self, disable_docs_url: bool = False) -> str:
        """
        Format scan result as JUnitXML.

        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        try:
            junit_renderer = JUnitXml()
            return junit_renderer.render(self.check_results, disable_docs_url)
        except xml.parsers.expat.ExpatError as e:
            print(f"Error: exporting JUnit XML failed: {e}.", file=sys.stderr)
            sys.exit(2)

    def format_sarif(self, disable_docs_url: bool = False) -> str:
        """Format scan result as Sarif."""
        sarif_render = SarifReport()
        return sarif_render.render(self.check_results, disable_docs_url)

    def format_output(
        self,
        errors: List[YamlErrorDetails],
        output_format: OutputFormat,
        disable_colors: bool = False,
        disable_docs_url: bool = False,
        disable_scan_url: bool = False,
        rewrite: bool = False,
    ) -> str:
        """
        Format scan result.

        :param output_format: Target output format
        :param disable_colors: Disable output colors and styling
        :param disable_docs_url: Disable outputting URL to documentation
        :param disable_scan_url: Disable outputting URL to scan result
        :param rewrite: Rewrite files with fixes
        :return: A formatted string
        """
        if output_format == OutputFormat.TEXT:
            return self._format_text(errors, disable_colors, disable_docs_url, disable_scan_url, rewrite)
        if output_format == OutputFormat.JSON:
            return self._format_json(disable_docs_url)
        if output_format == OutputFormat.YAML:
            return self._format_yaml(disable_docs_url)

        print(
            f"Error: unknown output format: {output_format}, "
            f"valid values are: {list(str(e) for e in OutputFormat)}.",
            file=sys.stderr,
        )
        sys.exit(2)

    def apply_check_result_suggestions(self, display_level: DisplayLevel, scan_paths: List[Path]) -> None:
        """
        Automatically apply suggestions.

        :param display_level: DisplayLevel object
        """
        all_suggestions = [cr.suggestion for cr in self.check_results if cr.suggestion is not None]
        applied_suggestions = set(update_files(all_suggestions, display_level, scan_paths))
        self.fixed_check_results = [
            cr for cr in self.check_results if cr.suggestion is not None and cr.suggestion in applied_suggestions
        ]
        fixed_set = set(self.fixed_check_results)
        self.check_results = [cr for cr in self.check_results if cr not in fixed_set]
