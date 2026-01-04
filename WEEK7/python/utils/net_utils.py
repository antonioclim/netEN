"""Utility helpers for Week 7 scripts.

This module aims to keep dependencies minimal and behaviour predictable.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class CmdResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_cmd(argv: Iterable[str], timeout: Optional[int] = None, check: bool = False, cwd: Optional[Path] = None) -> CmdResult:
    argv_list = list(argv)
    proc = subprocess.run(
        argv_list,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        cwd=str(cwd) if cwd else None,
    )
    res = CmdResult(argv=argv_list, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {shlex.join(argv_list)}\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}")
    return res


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_root() -> bool:
    return os.geteuid() == 0
