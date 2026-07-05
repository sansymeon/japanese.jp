"""KML long-hold framing policy — minimum per-scene safe scale via fill-safety audit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = Path(__file__).resolve().parent / "audit_fill_safety.py"

# Natural framing default: no authored zoom unless audit requires repair.
DEFAULT_IMAGE_SCALE = 1.0


def run_fill_safety_audit(collection_id: str, *, dry_run: bool = False) -> int:
    """Post-build audit: minimum safe imageScale per scene. Returns process exit code."""
    cmd = [sys.executable, str(AUDIT_SCRIPT), collection_id]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode
