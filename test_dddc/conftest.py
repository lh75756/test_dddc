import pytest


@pytest.fixture(scope='module')
def hello1():
    print("hello")