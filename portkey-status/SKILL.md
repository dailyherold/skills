---
name: portkey-status
description: Check Portkey model health with live API tests (basic + tool-use) and list virtual key budget limits. Always use this skill when the user asks about model availability, which providers are working, API latency, Portkey status, virtual key budgets or credits, or anything like "are my models up?", "check my providers", "which models are broken", "run portkey-status", or "test my portkey config". Also trigger when the user wants to validate their Portkey setup is functional or debug why a model isn't responding.
---

# Portkey Status

Scripts live in `scripts/` under this skill's base directory (shown at the top of this file). Always run with `uv run` from that directory.

## API key

Check for `$PORTKEY_API_KEY` in the environment first. If it's not set, ask the user where to find it — they may have it in a password manager, a secrets file, or a shell config. Don't assume any particular location.

```bash
echo ${PORTKEY_API_KEY:+set}  # check if set
```

## Run commands

```bash
SCRIPTS="<skill-base-dir>/scripts"

PORTKEY_API_KEY="..." uv --directory "$SCRIPTS" run python main.py check            # test all models
PORTKEY_API_KEY="..." uv --directory "$SCRIPTS" run python main.py check openai     # filter by substring
PORTKEY_API_KEY="..." uv --directory "$SCRIPTS" run python main.py credits          # list virtual key budgets
```

## Interpreting results

After running, reproduce the results as a markdown table in your response (don't just show raw terminal output). Then:

- **All passing** — confirm everything looks healthy and note any slow models (>5s latency worth flagging).
- **Some failing** — highlight the failing models and their error messages. Use the error text to guide debugging: 4xx errors usually mean a config or auth issue on that virtual key; 5xx means a provider-side problem; timeouts suggest the model may be rate-limited or overloaded. Suggest checking the relevant virtual key in the Portkey dashboard.
- **All failing** — likely an API key or connectivity issue rather than individual model problems. Check the key is valid and Portkey is reachable.

The `Tools` column shows whether the model supports function/tool calling — failures there specifically matter if the user's app relies on agentic use.

## Model config

Edit `scripts/config.py` to add, remove, or tweak models. Supported per-model fields:

| Field | Default | Purpose |
|---|---|---|
| `id` | required | Portkey virtual key slug, e.g. `@openai/gpt-5.4` |
| `endpoint` | `"chat"` | Set to `"responses"` for models needing the Responses API |
| `skip_temperature` | `false` | Omit `temperature` param (some models reject it) |
| `tokens_param` | `"max_tokens"` | Use `"max_completion_tokens"` for newer OpenAI models |
| `skip_tools` | `false` | Skip tool-use test for models that don't support it |
