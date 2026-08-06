from __future__ import annotations

from pathlib import Path
import sys

# Ensure src/ directory is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipelines.corruption_flow import main

if __name__ == "__main__":
    main()

