"""What the suite does when the browser its measurements need is missing.

The tests that measure a region in a real browser are only as good as their
guard. A guard that skips everywhere renders the same green checks page whether
those measurements were made or not, which is the state this file exists to
keep closed.

Its subject is the suite's own fixture rather than a module of the package,
which is why it is declared as a non-mirroring test in `pyproject.toml`.
"""

import pytest
from playwright.sync_api import Error

from tests.conftest import chromium

#: The fixture's own function, called directly. Asking for the fixture would
#: probe this machine's real browser, which is the thing being stood in for.
probe = chromium.__wrapped__


@pytest.fixture
def no_browser(monkeypatch):
    def launch_fails(*args, **kwargs):
        raise Error("Executable doesn't exist at ~/.cache/ms-playwright/chromium")

    monkeypatch.setattr("playwright.sync_api.sync_playwright", launch_fails)


class TestAMissingBrowser:
    def test_fails_on_ci(self, no_browser, monkeypatch):
        monkeypatch.setenv("CI", "true")

        try:
            probe()
        except pytest.skip.Exception as skipped:
            pytest.fail(
                f"a missing browser skipped on CI instead of failing: {skipped}",
                pytrace=False,
            )
        except pytest.fail.Exception as failure:
            message = str(failure)
        else:
            pytest.fail("a missing browser passed silently on CI", pytrace=False)

        assert "no chromium available" in message
        assert "install-playwright" in message, (
            "the failure has to name what is missing, or whoever hits it has "
            "to go and find out which input installs a browser"
        )

    def test_skips_off_ci(self, no_browser, monkeypatch):
        monkeypatch.delenv("CI", raising=False)

        with pytest.raises(pytest.skip.Exception) as skipped:
            probe()

        assert "no chromium available" in str(skipped.value)
