from pathlib import Path, PurePath
from dataclasses import dataclass
from typing import Generator, Dict

import pytest
import tomli

from clickzetta import connect
from clickzetta.dbapi.connection import Connection


_it_config_path = PurePath(__file__).parent.joinpath("integration_test.toml")
_it_config_existed = Path(_it_config_path).exists()


def pytest_configure(config):
    config.addinivalue_line("markers", "integration_test")


def pytest_runtest_setup(item):
    if item.get_closest_marker("integration_test") and not _it_config_existed:
        pytest.skip("skipping integration test because config file not found")


@pytest.fixture(scope="session")
def it_config() -> Dict:
    with open(_it_config_path, "rb") as f:
        config = tomli.load(f)
        return config


@pytest.fixture
def it_conn(it_config: Dict) -> Generator[Connection, None, None]:
    conn = connect(**it_config["connection"])
    yield conn
    conn.close()
