import os
from pathlib import Path

TESTS_HOME = Path(os.path.abspath(os.path.dirname(__file__)))

MINI_CEDA_CACHE_DIR = Path.home() / ".mini-ceda-archive"
MINI_CEDA_CACHE_BRANCH = "main"
MINI_BADC_DIR = MINI_CEDA_CACHE_DIR / MINI_CEDA_CACHE_BRANCH / "archive" / "badc"

data_files = TESTS_HOME / "testdata"
test_outputs = TESTS_HOME / "test_outputs"
cached_outputs = TESTS_HOME / "cached_outputs"


if not os.path.isdir(test_outputs):
    os.makedirs(test_outputs)

