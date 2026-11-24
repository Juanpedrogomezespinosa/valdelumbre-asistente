import hashlib
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[2] / "datos"

# Fingerprints of the files as delivered: they must never be edited (D-003).
ORIGINAL_SHA1 = {
    "pois.json": "af212003f98c208d9acd4d4968fe4951e2114135",
    "evaluacion.json": "19afe549d4508f1bbccd467fb8a079ab36d3b8f8",
}


@pytest.mark.parametrize(("file_name", "expected_sha1"), ORIGINAL_SHA1.items())
def test_source_data_is_unmodified(file_name: str, expected_sha1: str) -> None:
    content = (DATA_DIR / file_name).read_bytes()

    assert hashlib.sha1(content).hexdigest() == expected_sha1
