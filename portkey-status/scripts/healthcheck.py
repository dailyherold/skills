#!/usr/bin/env python3
"""Portkey model health checker — uses the Portkey Python SDK."""

import os
import sys
import time
import uuid
from typing import Optional

from portkey_ai import Portkey
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from config import MAX_TOKENS, MODELS, TEST_PROMPT

console = Console()

TOOL_DEF_CHAT = {
    "type": "function",
    "function": {
        "name": "test_fn",
        "description": "test",
        "parameters": {"type": "object", "properties": {}},
    },
}
TOOL_DEF_RESPONSES = {
    "type": "function",
    "name": "test_fn",
    "description": "test",
    "parameters": {"type": "object", "properties": {}},
}


def _get_client() -> Portkey:
    api_key = os.environ.get("PORTKEY_API_KEY") or input("Enter Portkey API key: ").strip()
    return Portkey(api_key=api_key, cache_force_refresh=True)


def _test_model(client: Portkey, model_cfg: dict, use_tools: bool) -> tuple[bool, float, str]:
    model_id = model_cfg["id"]
    endpoint = model_cfg.get("endpoint")
    tokens_param = model_cfg.get("tokens_param", "max_tokens")
    skip_temp = model_cfg.get("skip_temperature", False)

    c = client.with_options(
        trace_id=f"status-{uuid.uuid4().hex[:12]}",
        metadata={"test": "portkey-status", "tool_test": str(use_tools)},
    )

    start = time.perf_counter()
    try:
        if endpoint == "responses":
            kwargs: dict = {"model": model_id, "input": TEST_PROMPT, "max_output_tokens": MAX_TOKENS}
            if use_tools:
                kwargs["tools"] = [TOOL_DEF_RESPONSES]
            c.responses.create(**kwargs)
        else:
            kwargs = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": TEST_PROMPT},
                ],
                tokens_param: MAX_TOKENS,
            }
            if not skip_temp:
                kwargs["temperature"] = 0.0
            if use_tools:
                kwargs["tools"] = [TOOL_DEF_CHAT]
            c.chat.completions.create(**kwargs)

        return True, round(time.perf_counter() - start, 3), "OK"
    except Exception as e:
        return False, round(time.perf_counter() - start, 3), str(e)[:150]


def run(filter_arg: Optional[str] = None) -> None:
    client = _get_client()

    models = [m for m in MODELS if not filter_arg or filter_arg in m["id"]]
    if filter_arg:
        console.print(f"Filtering for: [yellow]{filter_arg}[/yellow]")

    console.print(f"\n[bold]Portkey Status — Model Health[/bold]")
    console.print(f"Testing [cyan]{len(models)}[/cyan] models...\n")

    results = []
    with Progress() as progress:
        task = progress.add_task("Testing...", total=len(models) * 2)
        for cfg in models:
            label = cfg["id"].split("/")[-1]

            progress.update(task, description=f"[basic] {label}")
            basic_ok, basic_lat, basic_msg = _test_model(client, cfg, use_tools=False)
            progress.advance(task)

            if cfg.get("skip_tools"):
                agent_ok, agent_lat, agent_msg = True, 0.0, "skipped"
            else:
                progress.update(task, description=f"[tools] {label}")
                agent_ok, agent_lat, agent_msg = _test_model(client, cfg, use_tools=True)
            progress.advance(task)

            results.append({
                "id": cfg["id"],
                "basic_ok": basic_ok,
                "agent_ok": agent_ok,
                "basic_lat": basic_lat,
                "msg": agent_msg if not agent_ok else basic_msg,
            })

    table = Table(title="Model Health")
    table.add_column("Model", style="cyan")
    table.add_column("Basic", justify="center")
    table.add_column("Tools", justify="center")
    table.add_column("Latency", justify="right")
    table.add_column("Note")

    passed = sum(1 for r in results if r["basic_ok"] and r["agent_ok"])
    for r in results:
        ok = r["basic_ok"] and r["agent_ok"]
        table.add_row(
            r["id"],
            "✅" if r["basic_ok"] else "❌",
            "✅" if r["agent_ok"] else "❌",
            f"{r['basic_lat']:.2f}s",
            "" if ok else r["msg"][:80],
        )

    console.print(table)
    console.print(f"\n[bold]{'✅' if passed == len(results) else '⚠️'} {passed}/{len(results)} passed[/bold]\n")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
