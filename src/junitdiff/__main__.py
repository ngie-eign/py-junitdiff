"""JUnitDiff CLI."""

from __future__ import annotations

import argparse
import logging

from junitparser import JUnitXml

# ruff: noqa: T201


# import enum
# class DiffLevel(enum.Enum):
#    TEST_SUITE = enum.auto()
#    TEST_CASE = enum.auto()


def diff_runs_at_testsuite_level(
    run1: JUnitXml, run2: JUnitXml,
) -> tuple[set[tuple[str, str], ...]]:
    run1_results = set()
    for suite in run1:
        for case in suite:
            run1_results.add(((suite.name, case.name), case.result))
    run2_results = {
        ((suite.name, case.name), case.result) for suite in run2 for case in suite
    }
    return run2_results - run1_results, run1_results - run2_results


def diff_runs_at_testcase_level(
    run1: JUnitXml, run2: JUnitXml,
) -> tuple[set[tuple[str, str], ...]]:
    run1_results = set()
    for suite in run1:
        print(suite.name)
        for case in suite:
            print(case.name)
            run1_results.add(((suite.name, case.name), case.result))
    run2_results = {
        ((suite.name, case.name), case.result) for suite in run2 for case in suite
    }
    return run2_results - run1_results, run1_results - run2_results


def main(argv: list[str] | None = None) -> None:
    """Eponymous main."""
    logging.basicConfig(
        format="%(filename)s: %(levelname)s: %(message)s", level=logging.INFO,
    )
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--diff-level", choices=("test-suite", "test-case"))
    argparser.add_argument("run1_xml", type=argparse.FileType("r"))
    argparser.add_argument("run2_xml", type=argparse.FileType("r"))
    args = argparser.parse_args(args=argv)

    run1_xml = JUnitXml.fromfile(args.run1_xml)
    run2_xml = JUnitXml.fromfile(args.run2_xml)

    if args.diff_level == "test-case":
        diff_between_run2_and_run1_xml = diff_runs_at_testcase_level(run1_xml, run2_xml)
    else:
        diff_between_run2_and_run1_xml = diff_runs_at_testsuite_level(run1_xml, run2_xml)

    print(diff_between_run2_and_run1_xml)


if __name__ == "__main__":
    main()
