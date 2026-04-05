import pytest


@pytest.fixture
def _db_access(db):
    """Shortcut fixture for tests that need database access."""
