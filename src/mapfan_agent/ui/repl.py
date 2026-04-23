"""Interactive REPL with HTTP streaming."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from mapfan_agent.client import MapfanClient
from mapfan_agent.ui.output import print_error

console = Console()


async def run_repl(client: MapfanClient) -> None:
    """Run interactive REPL loop via HTTP API.

    Args:
        client: MapfanClient connected to the API server.
    """
    healthy = await client.health()
    if not healthy:
        print_error(f"Cannot connect to API server at {client.api_url}")
        return

    console.print(
        f"[bold]mapfan-agent[/bold] (REPL mode) — "
        f"connected to [cyan]{client.api_url}[/cyan]\n"
        f"Type [bold]exit[/bold] or [bold]quit[/bold] to leave.\n"
    )

    task_id: str | None = None

    while True:
        try:
            query = Prompt.ask("[bold cyan]>[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye!")
            break

        query = query.strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            console.print("Bye!")
            break

        try:
            # Use streaming for real-time output
            console.print()
            full_response = ""
            async for event, data in client.chat_stream(query, task_id=task_id):
                if event == "task_id":
                    task_id = data
                elif event == "token":
                    console.print(data, end="")
                    full_response += data
                elif event == "done":
                    break
            console.print("\n")
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/dim]")
            continue
        except Exception as e:
            print_error(str(e))
            continue
