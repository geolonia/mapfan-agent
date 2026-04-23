"""Rich console output helpers."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown

console = Console()


def format_agent_response(text: str) -> str:
    """Extract and return the displayable text from agent response."""
    return text.strip()


def format_error(message: str) -> str:
    """Format an error message."""
    return f"Error: {message}"


def extract_text_content(content: str | list) -> str:
    """Extract text from message content.

    Claude API may return content as a list of blocks
    (e.g. [{"type": "text", "text": "..."}]) instead of a plain string.
    """
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts).strip()
    return str(content).strip()


def print_response(content: str | list) -> None:
    """Print agent response as markdown to console."""
    text = extract_text_content(content)
    console.print(Markdown(text))


def print_error(message: str) -> None:
    """Print error message to console."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_streaming_token(token: str) -> None:
    """Print a single streaming token without newline."""
    console.print(token, end="")
