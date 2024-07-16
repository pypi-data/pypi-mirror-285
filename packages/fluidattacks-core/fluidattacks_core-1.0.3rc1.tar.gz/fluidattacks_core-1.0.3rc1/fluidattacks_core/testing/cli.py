from .plugins import (
    CustomFixturesPlugin,
)
import argparse as _argparse
import os as _os
import pytest as _pytest
import sys as _sys
from typing import (
    cast,
)


def execute() -> None:
    parser = _argparse.ArgumentParser(
        prog="fluidattacks-test",
        description=(
            "🏹 Python package for unit and integration testing through "
            "Fluid Attacks projects 🏹"
        ),
    )
    parser.add_argument(
        "--target",
        metavar="TARGET",
        type=str,
        default="",
        help="Folder to start the tests. Default is current folder.",
        nargs="?",
    )

    parser.add_argument(
        "--src",
        metavar="SRC",
        type=str,
        default="src",
        help="The source code for coverage report. Default is src.",
        nargs="?",
    )

    parser.add_argument(
        "--scope",
        metavar="SCOPE",
        type=str,
        help="Type and module to test.",
    )
    args = parser.parse_args()

    target = cast(str, args.target if args.target else _os.getcwd())

    test_path = _os.path.join(target, "test")
    if not _os.path.isdir(test_path):
        raise FileExistsError(f"Test folder not found: {test_path}")

    cov_path = _os.path.join(target, args.src)
    if not _os.path.isdir(cov_path):
        raise FileExistsError(f"Source folder not found: {cov_path}")

    unit_tests_path = _os.path.join(test_path, "unit/src")
    if not _os.path.isdir(unit_tests_path):
        raise FileExistsError("Unit tests folder not found (test/unit/src)")

    unit_test_groups = [
        path
        for path in _os.listdir(unit_tests_path)
        if _os.path.isdir(_os.path.join(unit_tests_path, path))
    ]

    scope = args.scope
    if scope not in unit_test_groups:
        raise ValueError(f"Group not found: {scope}")

    _coverage_args = (
        [
            "--cov",
            f"{cov_path}",
            "--cov-branch",
            "--cov-report",
            "term",
            "--no-cov-on-fail",
        ]
        if cov_path
        else []
    )

    _pytest_args = [
        *_coverage_args,
        "--disable-warnings",
        "--showlocals",
        "--strict-markers",
        *(["-m", f"{scope}"] if scope else []),
        "-rfs",
        "-vvl",
    ]
    _sys.exit(
        _pytest.main(
            [unit_tests_path, *_pytest_args],
            plugins=[
                CustomFixturesPlugin(),
            ],
        )
    )
