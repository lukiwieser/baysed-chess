"""Remove files created when testing lichess_bot."""
import shutil
import os
from typing import Any


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """Remove files created when testing lichess_bot."""
    shutil.copyfile("lib/correct_lichess.py", "lib/lichess.py")
    os.remove("lib/correct_lichess.py")
    if os.path.exists("TEMP") and not os.getenv("GITHUB_ACTIONS"):
        shutil.rmtree("TEMP")
    if os.path.exists("logs"):
        shutil.rmtree("logs")
