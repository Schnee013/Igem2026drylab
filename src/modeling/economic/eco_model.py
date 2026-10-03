"""Run the Spanish protected-tomato nematode economic demo.

The implementation lives in ``src.modeling.economic.eco_model_pkg`` so it can
also be invoked with ``python -m src.modeling.economic.eco_model_pkg.cli``.
"""

from __future__ import annotations

from pathlib import Path
import sys


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.economic.eco_model_pkg.cli import main
else:
    from .eco_model_pkg.cli import main


if __name__ == "__main__":
    main()
