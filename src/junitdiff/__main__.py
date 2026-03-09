"""JUnitDiff CLI."""
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import argparse
import enum
import pathlib
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
class ElementKey:
    """A representation of the name for a given element.

    This object exists as a 'uniquifier' for `dict` keys.
    """

    name: str
    classname: str | None = None

    def __hash__(self) -> int:
        """hash(..) magic method.

        The order is computed this way since `self.classname` has precedence
        over `self.name`.
        """
        return hash((self.classname, self.name))


@dataclass
class FilteredResult:
    """Provide filtered fields for `junitparser.Element` for deepdiff."""

    errors: int
    failures: int
    skipped: int
    tests: int


def element_key(elem: junitparser.Element) -> ElementKey:
    """Build an `ElementKey` from a `junitparser.Element` object.

    Args:
        elem: a target `junitparser.Element` to build an `ElementKey` from.

    Returns:
        An `ElementKey` representing the "uniquifier

    """
    if isinstance(elem, junitparser.TestCase):
        return ElementKey(name=elem.name, classname=elem.classname)
    if isinstance(elem, junitparser.TestSuite):
        return ElementKey(name=elem)
    # ruff: noqa: SLF001
    err_msg = f"Unsupported type: {elem._tag}"
    raise NotImplementedError(err_msg)


def flatten_elements(
    run_output: JUnitXml,
    junit_type: junitparser.Element,
) -> dict[ElementKey, junitparser.Element]:
    """Flatten out elements of a particular type, `junit_type`, from `run`.

    Args:
        run_output: JUnit XML output.
        junit_type: `Element` type to parse out, e.g., `junitparser.TestCase`.

    Returns:
        A list of filtered `Elements` of a selected type, keyed by their respective
        names.

    """
    return {
        element_key(elem): filter_properties(elem)
        for elem in run_output.iterchildren(junit_type)
    }


def filter_properties(
    elem: junitparser.Element,
) -> FilteredResult:
    """Filter out properties from `elem`.

    Args:
        name: the "uniquifier" for `elem` (precomputed to avoid computing again).
        elem: a root element to parse results from.

    Returns:
        A list of filtered results.

    """
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
    elif isinstance(elem, junitparser.TestSuite):
        errors = elem.errors
        failures = elem.failures
        skipped = elem.skipped
        tests = elem.tests
    else:
        # ruff: noqa: SLF001
        err_msg = f"Unsupported type: {elem._tag}"
        raise NotImplementedError(err_msg)

    return FilteredResult(
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
    argparser.add_argument("run1_xml")
    argparser.add_argument("run2_xml")
    args = argparser.parse_args(args=argv)

    run1_xml = JUnitXml.fromstring(pathlib.Path(args.run1_xml).read_text())
    run2_xml = JUnitXml.fromstring(pathlib.Path(args.run2_xml).read_text())

    if args.diff_level == "testcase":
        junit_result_type = junitparser.TestCase
    else:
        junit_result_type = junitparser.TestSuite

    run1_results = flatten_elements(run1_xml, junit_result_type)
    run2_results = flatten_elements(run2_xml, junit_result_type)

    differ = deepdiff.DeepDiff(run1_results, run2_results)
    if differ:
        print(f"Differences exist:\n{pprint.pformat(differ)}")
        return DiffExitCode.DIFF
    print("No noticeable differences")
    return DiffExitCode.NO_DIFF


def main(argv: ... = None) -> int:
    """Eponymous main (outer)."""
    try:
        return _main(argv=argv)
    # ruff: noqa: BLE001
    except Exception:
        traceback.print_exc()
        return DiffExitCode.ERROR


if __name__ == "__main__":
    sys.exit(main())
