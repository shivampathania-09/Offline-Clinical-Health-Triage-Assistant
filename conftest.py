import sys
from pathlib import Path

# Automatically ensure project root is in sys.path for all pytest test runs
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
