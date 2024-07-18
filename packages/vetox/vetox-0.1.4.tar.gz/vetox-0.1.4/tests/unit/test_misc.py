# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Miscellaneous tests for the `vetox` tool."""

from __future__ import annotations

import subprocess
import sys
import typing

import pytest


if typing.TYPE_CHECKING:
    from typing import Final


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["features", "--help"],
        ["run", "--help"],
        ["run-parallel", "--help"],
        ["version", "--help"],
        ["features"],
        ["version"],
    ],
)
def test_cmdline_good(args: list[str]) -> None:
    """Success, some output, no error messages."""
    res: Final = subprocess.run(
        [sys.executable, "-m", "vetox", *args],
        capture_output=True,
        check=False,
        encoding="UTF-8",
    )
    assert not res.returncode, repr(res)
    assert res.stdout is not None, repr(res)
    assert res.stdout, repr(res)
    assert res.stderr is not None, repr(res)
    assert not res.stderr, repr(res)


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["nosuchcommand"],
        ["--nosuchoption"],
        ["features", "--nosuchoption"],
        ["run", "--nosuchoption"],
        ["run-parallel", "--nosuchoption"],
        ["version", "--nosuchoption"],
    ],
)
def test_cmdline_bad(args: list[str]) -> None:
    """Failure, no output, some error messages."""
    res: Final = subprocess.run(
        [sys.executable, "-m", "vetox", *args],
        capture_output=True,
        check=False,
        encoding="UTF-8",
    )
    assert res.returncode, repr(res)
    assert res.stdout is not None, repr(res)
    assert not res.stdout, repr(res)
    assert res.stderr is not None, repr(res)
    assert res.stderr, repr(res)
