import os
from pathlib import Path
from unittest import TestCase

import pytest

from e2clab.log import init_logging


class TestE2cLab(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        # Setup path to test files
        self.test_folder = Path(__file__).resolve().parent.parent / "test_files"
        # Silence file loggers
        init_logging(file_handler=False)
        super().__init__(methodName)

    @staticmethod
    def skip_on_runner():
        r = os.getenv("RUNNER_SKIP_PYTEST")
        skip = r is not None
        return pytest.mark.skipif(skip, reason="Can-t run this test on gitlab runner")
