import sys
from pathlib import Path

# The updater lives beside this package, in the repository's root.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.append(str(_ROOT))

from .cli import main  # noqa: E402

raise SystemExit(main())
