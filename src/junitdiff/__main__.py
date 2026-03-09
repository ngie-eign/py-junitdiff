"""JUnitDiff CLI."""
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import argparse
import enum
import pprint
import sys
import traceback
from dataclasses import dataclass

import deepdiff
import junitparser
from junitparser import JUnitXml

# ruff: noqa: T201


class DiffExitCode(enum.IntEnum):
    """Exit code to return.

    This matches `EXIT CODE` of many other diff-like utilities.
    """

    NO_DIFF = 0
    DIFF = 1
    ERROR = 2


@dataclass
class FilteredResult:
    """Provide filtered fields for `junitparser.Element` for deepdiff."""

    name: list[str]
    errors: int
    failures: int
    skipped: int
    tests: int


def flatten_elements(
    run_output: JUnitXml,
    junit_type: junitparser.Element,
) -> list[junitparser.Element]:
    """Flatten out elements of a particular type, `junit_type`, from `run`.

    Args:
        run_output: JUnit XML output.
        junit_type: `Element` type to parse out, e.g., `junitparser.TestCase`.

    Returns:
        A list of filtered `Elements` of a selected type.

    """
    return list(run_output.iterchildren(junit_type))


def filter_properties(elem: junitparser.Element) -> list[FilteredResult]:
    """Filter out properties from `elem`.

    Args:
        elem: a root element to parse results from.

    Returns:
        A list of filtered results.

    """
    name: list[str] = []
    errors = failures = skipped = tests = 0
    if isinstance(elem, junitparser.TestCase):
        tests = 1
        for res in elem.result:
            if isinstance(res, junitparser.Error):
                errors += 1
            elif isinstance(res, junitparser.Failure):
                failures += 1
            elif isinstance(res, junitparser.Skipped):
                skipped += 1
        name = [elem.name]
        if elem.classname is None:
            name.append(elem.classname)
    elif isinstance(elem, junitparser.TestSuite):
        name = [elem.name]
        errors = elem.errors
        failures = elem.failures
        skipped = elem.skipped
        tests = elem.tests
    else:
        # ruff: noqa: SLF001
        err_msg = f"Unsupported type: {elem._tag}"
        raise NotImplementedError(err_msg)

    return FilteredResult(
        name,
        errors,
        failures,
        skipped,
        tests,
    )


def _main(argv: list[str] | None = None) -> int:
    """Eponymous main (inner)."""
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--diff-level",
        choices=("testcase", "testsuite"),
        default="testcase",
        help="Level to compare from.",
    )
    argparser.add_argument("run1_xml", type=argparse.FileType("r"))
    argparser.add_argument("run2_xml", type=argparse.FileType("r"))
    args = argparser.parse_args(args=argv)

    run1_xml = JUnitXml.fromfile(args.run1_xml)
    run2_xml = JUnitXml.fromfile(args.run2_xml)

    if args.diff_level == "testcase":
        junit_result_type = junitparser.TestCase
    else:
        junit_result_type = junitparser.TestSuite

    run1_results = flatten_elements(run1_xml, junit_result_type)
    run2_results = flatten_elements(run2_xml, junit_result_type)

    res1_filtered = [filter_properties(a) for a in run1_results]
    res2_filtered = [filter_properties(b) for b in run2_results]
    differ = deepdiff.DeepDiff(res1_filtered, res2_filtered)
    if differ:
        print(f"Differences exist:\n{pprint.pformat(differ)}")
        return DiffExitCode.DIFF
    print("No noticeable differences")
    return DiffExitCode.NO_DIFF


def main(argv: ... = None) -> int:
    """Eponymous main (outer)."""
    try:
        sys.exit(_main(argv=argv))
    # ruff: noqa: BLE001
    except Exception:
        traceback.print_exc()
        sys.exit(DiffExitCode.ERROR)


if __name__ == "__main__":
    main()
