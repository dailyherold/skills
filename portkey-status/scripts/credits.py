#!/usr/bin/env python3
"""
Portkey virtual key budget / usage limits.

Shows Portkey-side usage_limits configured on your virtual keys.

Provider credit balances (actual account credits) require separate provider
API calls — not yet implemented. Future extension points:
  - OpenAI:     GET https://api.openai.com/v1/organization/usage
  - Anthropic:  no public credits API currently available
  - Google:     Cloud Billing API
  - xAI/Grok:   no public credits API currently available
  - Fireworks:  check their dashboard/API
"""

import os

from portkey_ai import Portkey
from rich.console import Console
from rich.table import Table

console = Console()


def run() -> None:
    api_key = os.environ.get("PORTKEY_API_KEY") or input("Enter Portkey API key: ").strip()
    client = Portkey(api_key=api_key)

    console.print("\n[bold]Portkey Status — Virtual Key Budgets[/bold]\n")

    resp = client.virtual_keys.list()
    vkeys = resp.data or []

    if not vkeys:
        console.print("[yellow]No virtual keys found.[/yellow]")
        return

    table = Table(title=f"Virtual Keys ({len(vkeys)} total)")
    table.add_column("Name", style="cyan")
    table.add_column("Provider")
    table.add_column("Usage Limits")
    table.add_column("Slug", style="dim")

    for vk in vkeys:
        limits = vk.get("usage_limits") or {}
        limits_str = ", ".join(f"{k}: {v}" for k, v in limits.items()) if limits else "—"
        table.add_row(
            vk.get("name", ""),
            vk.get("provider", ""),
            limits_str,
            vk.get("slug", ""),
        )

    console.print(table)
    console.print(
        "\n[dim]Provider-level credit balances require direct provider API calls"
        " — extend credits.py when needed.[/dim]\n"
    )


if __name__ == "__main__":
    run()
