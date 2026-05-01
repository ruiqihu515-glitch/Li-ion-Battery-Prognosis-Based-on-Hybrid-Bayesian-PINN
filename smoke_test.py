#!/usr/bin/env python3
"""Lightweight smoke test for repository reproduction readiness.

Checks:
1) Python version
2) Dependency import status
3) Data path resolution from TF/battery_data.py (with optional overrides)
4) Expected NASA .mat files presence
5) Key module import sanity
"""

from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from pathlib import Path

REQUIRED_MODULES = ["numpy", "scipy", "matplotlib", "pandas", "sklearn", "tensorflow"]
KEY_MODULES = ["BatteryModels", "BatteryParameters", "TF.battery_data"]


def parse_battery_data_config(repo_root: Path):
    text = (repo_root / "TF" / "battery_data.py").read_text(encoding="utf-8")
    data_path_match = re.search(r"DATA_PATH\s*=\s*'([^']+)'", text)
    if not data_path_match:
        raise RuntimeError("Could not parse DATA_PATH in TF/battery_data.py")
    data_path = data_path_match.group(1)
    entries = re.findall(r"\s*(\d+):\s*'([^']+)'", text)
    if not entries:
        raise RuntimeError("Could not parse BATTERY_FILES in TF/battery_data.py")
    return data_path, [(int(k), v) for k, v in entries]


def resolve_data_root(repo_root: Path, default_data_path: str, cli_data_root: str | None) -> tuple[Path, str]:
    if cli_data_root:
        return Path(cli_data_root).expanduser().resolve(), "--data-root"

    env_data_root = os.environ.get("BATTERY_DATA_ROOT")
    if env_data_root:
        return Path(env_data_root).expanduser().resolve(), "BATTERY_DATA_ROOT"

    default_root = (repo_root / "TF" / default_data_path).resolve()
    return default_root, "TF/battery_data.py:DATA_PATH"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test for reproduction readiness")
    parser.add_argument(
        "--data-root",
        type=str,
        default=None,
        help="Override data root directory (highest precedence).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    print("== Smoke Test: Li-ion Battery Hybrid Bayesian PINN ==")
    print(f"Repo root: {repo_root}")
    print(f"Python: {sys.version.split()[0]}")

    print("\n[1] Dependency imports")
    dep_ok = True
    for mod in REQUIRED_MODULES:
        try:
            m = importlib.import_module(mod)
            print(f"  OK   {mod:<12} version={getattr(m, '__version__', 'unknown')}")
        except Exception as exc:
            dep_ok = False
            print(f"  FAIL {mod:<12} {type(exc).__name__}: {exc}")

    print("\n[2] Data path and expected NASA files")
    data_path, entries = parse_battery_data_config(repo_root)
    data_root, source = resolve_data_root(repo_root, data_path, args.data_root)
    print(f"  DATA_PATH (from code): {data_path}")
    print(f"  Selected data root source: {source}")
    print(f"  Final data root in use: {data_root}")

    missing = []
    for rw, pattern in entries:
        fpath = data_root / pattern.format(rw)
        exists = fpath.exists()
        print(f"  RW{rw:<2} -> {fpath} [{'OK' if exists else 'MISSING'}]")
        if not exists:
            missing.append(fpath)

    print("\n[3] Key module imports")
    import_ok = True
    for mod in KEY_MODULES:
        try:
            importlib.import_module(mod)
            print(f"  OK   {mod}")
        except Exception as exc:
            import_ok = False
            print(f"  FAIL {mod} {type(exc).__name__}: {exc}")

    print("\n== Summary ==")
    print(f"Dependency status: {'OK' if dep_ok else 'INCOMPLETE'}")
    print(f"Missing NASA .mat files: {len(missing)}")
    print(f"Key module imports: {'OK' if import_ok else 'INCOMPLETE'}")

    return 0 if dep_ok and import_ok and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
