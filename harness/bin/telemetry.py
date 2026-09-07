"""Session telemetry: list-price costing, and a fallback for killed sessions.

A wall-clock kill can take the CLI down before it emits its final `result`
event, so `num_turns` and `total_cost_usd` are lost for exactly the runs that
consumed the most of both. Everything except output tokens can be recovered
exactly by re-summing the per-message `usage` in the stream; output tokens are
estimated (see estimate_output_tokens).
"""

# List price per MTok: (input, output, cache-read multiplier). Cache writes cost
# 1.25x the input rate on the 5-minute TTL and 2x on the 1-hour TTL.
PRICES = {
    "claude-sonnet-5":  (2.0, 10.0, 0.1),
    "claude-opus-5":    (5.0, 25.0, 0.1),
    "claude-fable-5-1": (10.0, 50.0, 0.025),
}
DEFAULT_MODEL = "claude-sonnet-5"

# Non-thinking output tokens per character of emitted text plus tool-call JSON.
# Fitted over the 852 sessions of runs/full that kept their result event:
# aggregate 0.5457, per-run median 0.5546 (p5 0.455, p95 0.649).
TOKENS_PER_CHAR = 0.5457


def cost_usd(model, input_tokens=0, output_tokens=0, cache_read=0,
             cache_write_5m=0, cache_write_1h=0):
    pin, pout, cread = PRICES.get(model, PRICES[DEFAULT_MODEL])
    return (input_tokens * pin
            + output_tokens * pout
            + cache_read * pin * cread
            + cache_write_5m * pin * 1.25
            + cache_write_1h * pin * 2.0) / 1e6


def estimate_output_tokens(thinking_delta, text_chars, tool_chars):
    """Output tokens for a session with no result event.

    `thinking_delta` is the sum of the stream's `thinking_tokens`
    system events, which the CLI emits as running per-message estimates. Summed
    over a session it tracks the billed thinking tokens closely: over the 831
    runs/full sessions that reported both, the ratio was 1.003 in aggregate and
    0.99-1.02 per run once a session exceeded 5k thinking tokens. It overshoots
    by up to 7x on sessions below that, where the dollar error is negligible.
    The visible remainder -- assistant text and tool-call arguments -- is
    converted with TOKENS_PER_CHAR.
    """
    return int(round(thinking_delta + TOKENS_PER_CHAR * (text_chars + tool_chars)))
