import json

import pytest


@pytest.mark.skip("api ratelimit")
def test_gsheets_download(invoke_cli):
    stdout = invoke_cli(
        [
            "gsheets://1vgx-ABiDI7kyO2-UgXlXiKcKN9ATKLb6SN-eZC2D50Y/Sheet1",
            "-o",
            "json://-",
        ]
    )
    assert json.loads(stdout) == [
        {"col a": "zz1", "col b": "zz2"},
        {"col a": "zz3", "col b": "zz4"},
    ]
