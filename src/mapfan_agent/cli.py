"""CLI entrypoint: ask and repl modes (thin HTTP client)."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console

from mapfan_agent import __version__
from mapfan_agent.config import load_config
from mapfan_agent.ui.output import print_response, print_error

load_dotenv()
console = Console()

app = typer.Typer(
    name="mapfan-agent",
    help="CLI for MapFan geospatial AI agent services.",
    add_completion=False,
    no_args_is_help=True,
)


def version_callback(value: bool):
    if value:
        typer.echo(f"mapfan-agent {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    """MapFan AI Agent CLI — query geospatial services via natural language."""
    pass


@app.command()
def ask(
    query: str = typer.Argument(..., help="Natural language query"),
    api_url: Optional[str] = typer.Option(None, "--api-url", help="API server URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to config.toml",
    ),
):
    """Run a single query and print the result."""
    asyncio.run(_run_query(query, api_url, api_key, config_path))


async def _run_query(
    query: str,
    api_url: str | None,
    api_key: str | None,
    config_path: str | None,
) -> None:
    """Execute a single query via HTTP API."""
    from pathlib import Path
    from mapfan_agent.client import MapfanClient

    config = load_config(
        config_path=Path(config_path) if config_path else None,
    )
    client = MapfanClient(
        api_url=api_url or config.api_url,
        api_key=api_key or config.api_key,
    )

    healthy = await client.health()
    if not healthy:
        print_error(f"Cannot connect to API server at {client.api_url}")
        raise typer.Exit(1)

    console.print(f"[dim]Querying: {query}[/dim]")
    try:
        result = await client.chat(query)
        print_response(result.response)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def repl(
    api_url: Optional[str] = typer.Option(None, "--api-url", help="API server URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to config.toml",
    ),
):
    """Start interactive REPL mode."""
    asyncio.run(_run_repl(api_url, api_key, config_path))


async def _run_repl(
    api_url: str | None,
    api_key: str | None,
    config_path: str | None,
) -> None:
    """Launch interactive REPL session via HTTP API."""
    from pathlib import Path
    from mapfan_agent.client import MapfanClient
    from mapfan_agent.ui.repl import run_repl

    config = load_config(
        config_path=Path(config_path) if config_path else None,
    )
    client = MapfanClient(
        api_url=api_url or config.api_url,
        api_key=api_key or config.api_key,
    )
    await run_repl(client)
