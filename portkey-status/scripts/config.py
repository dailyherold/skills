"""
Model configuration for portkey-status.

Edit MODELS below with your own Portkey virtual key slugs (found in app.portkey.ai/virtual-keys).
Each entry is a dict with `id` (Portkey virtual key slug) plus optional overrides:
  endpoint        "responses" → use Portkey Responses API instead of Chat Completions
  skip_temperature  omit temperature param (some models reject it)
  tokens_param    "max_completion_tokens" vs default "max_tokens"
  skip_tools      skip the tool-use test (model doesn't support it)
"""

MODELS = [
    {"id": "@claude/claude-haiku-4-5-20251001"},
    {"id": "@claude/claude-opus-4-6"},
    {"id": "@claude/claude-sonnet-4-6"},
    {"id": "@fireworks/accounts/fireworks/models/kimi-k2p5"},
    {"id": "@gemini/gemini-2.5-flash-lite"},
    {"id": "@gemini/gemini-2.5-pro"},
    {"id": "@gemini/gemini-3.1-flash-lite-preview"},
    {"id": "@gemini/gemini-3.1-pro-preview"},
    {"id": "@grok/grok-4-1-fast-reasoning"},
    {"id": "@grok/grok-4.20"},
    {"id": "@grok/grok-4.20-multi-agent", "endpoint": "responses", "skip_tools": True},
    {"id": "@grok/grok-4.20-reasoning"},
    {"id": "@openai/gpt-5-mini", "skip_temperature": True, "tokens_param": "max_completion_tokens"},
    {"id": "@openai/gpt-5.4", "tokens_param": "max_completion_tokens"},
    {"id": "@openai/gpt-5.4-pro", "endpoint": "responses", "tokens_param": "max_completion_tokens"},
]

TEST_PROMPT = "Say OK in one word."
MAX_TOKENS = 16
