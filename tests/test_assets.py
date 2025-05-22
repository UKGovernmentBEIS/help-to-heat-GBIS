import os

import pytest


@pytest.mark.parametrize(
    "filepath",
    [
        "./static/govuk-frontend/govuk-frontend-4.9.0.min.js",
        "./static/govuk-frontend/govuk-frontend-4.9.0.min.css",
    ],
)
def test_expected_gds_assets_files_exist(filepath):
    # this test asserts that the current GDS assets exist
    # if when updating the GDS assets this test fails, make sure to follow the README in
    # ./static/govuk-frontend/README.md
    # then, update this test to reference the new version's assets
    # otherwise we risk subtle issues with referenced assets not being found
    assert os.path.exists(filepath) is True
