import os
import pytest
from autosubmit_api.common.utils import JobSection
from autosubmit_api.config.confConfigStrategy import confConfigStrategy
from autosubmit_api.config.basicConfig import APIBasicConfig

from autosubmit_api.config.config_common import AutosubmitConfigResolver
from autosubmit_api.config.ymlConfigStrategy import ymlConfigStrategy
from tests.conftest import FAKE_EXP_DIR

from tests.custom_utils import custom_return_value


class TestBasicConfig:
    def test_api_basic_config(self, fixture_mock_basic_config):
        APIBasicConfig.read()

        assert os.getenv("AUTOSUBMIT_CONFIGURATION") == os.path.join(
            FAKE_EXP_DIR, ".autosubmitrc"
        )
        assert APIBasicConfig.LOCAL_ROOT_DIR == FAKE_EXP_DIR
        assert APIBasicConfig.DB_FILE == "autosubmit.db"
        assert APIBasicConfig.DB_PATH == os.path.join(
            FAKE_EXP_DIR, APIBasicConfig.DB_FILE
        )
        assert APIBasicConfig.AS_TIMES_DB == "as_times.db"
        assert APIBasicConfig.JOBDATA_DIR == os.path.join(
            FAKE_EXP_DIR, "metadata", "data"
        )
        assert APIBasicConfig.GLOBAL_LOG_DIR == os.path.join(FAKE_EXP_DIR, "logs")
        assert APIBasicConfig.STRUCTURES_DIR == os.path.join(
            FAKE_EXP_DIR, "metadata", "structures"
        )
        assert APIBasicConfig.HISTORICAL_LOG_DIR == os.path.join(
            FAKE_EXP_DIR, "metadata", "logs"
        )

        assert APIBasicConfig.GRAPHDATA_DIR == os.path.join(
            FAKE_EXP_DIR, "metadata", "graph"
        )

class TestConfigResolver:
    def test_simple_init(self, monkeypatch: pytest.MonkeyPatch):
        # Conf test decision
        monkeypatch.setattr(os.path, "exists", custom_return_value(True))
        monkeypatch.setattr(confConfigStrategy, "__init__", custom_return_value(None))
        resolver = AutosubmitConfigResolver("----", APIBasicConfig, None)
        assert isinstance(resolver._configWrapper, confConfigStrategy)

        # YML test decision
        monkeypatch.setattr(os.path, "exists", custom_return_value(False))
        monkeypatch.setattr(ymlConfigStrategy, "__init__", custom_return_value(None))
        resolver = AutosubmitConfigResolver("----", APIBasicConfig, None)
        assert isinstance(resolver._configWrapper, ymlConfigStrategy)

    def test_files_init_conf(self, fixture_mock_basic_config):
        resolver = AutosubmitConfigResolver("a3tb", fixture_mock_basic_config, None)
        assert isinstance(resolver._configWrapper, confConfigStrategy)


class TestYMLConfigStrategy:
    def test_exclusive(self, fixture_mock_basic_config):
        wrapper = ymlConfigStrategy("a007", fixture_mock_basic_config)
        assert True == wrapper.get_exclusive(JobSection.SIM)

        wrapper = ymlConfigStrategy("a003", fixture_mock_basic_config)
        assert False == wrapper.get_exclusive(JobSection.SIM)
