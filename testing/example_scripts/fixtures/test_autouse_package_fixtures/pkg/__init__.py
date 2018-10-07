import pytest

values = []


@pytest.fixture(autouse=True)
def setup():
    values.append("setup")
    yield
    del values[0]
