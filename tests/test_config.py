from pathlib import Path
from mapfan_agent.config import load_config, Config


def test_default_config():
    config = load_config(config_path=None, env_overrides={})
    assert config.api_url == "http://localhost:8000"
    assert config.api_key == ""


def test_env_overrides():
    env = {
        "MAPFAN_API_URL": "https://api.example.com",
        "MAPFAN_API_KEY": "test-key-123",
    }
    config = load_config(config_path=None, env_overrides=env)
    assert config.api_url == "https://api.example.com"
    assert config.api_key == "test-key-123"


def test_toml_config(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""\
[api]
url = "https://custom.example.com"
key = "toml-key"
""")
    config = load_config(config_path=config_file, env_overrides={})
    assert config.api_url == "https://custom.example.com"
    assert config.api_key == "toml-key"
