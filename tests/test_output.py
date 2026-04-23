from io import StringIO

from rich.console import Console

from mapfan_agent.ui.output import format_agent_response, format_error


def test_format_agent_response():
    """format_agent_response returns the text content of an AI message."""
    result = format_agent_response("東京タワーの緯度は35.658です。")
    assert "東京タワー" in result
    assert "35.658" in result


def test_format_error():
    """format_error wraps message in error styling."""
    result = format_error("接続に失敗しました")
    assert "接続に失敗しました" in result
