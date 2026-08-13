"""A small GreenSplit plugin that counts today's resets.

This file is intentionally detailed. It is meant to be useful as a starting
point for people writing their first GreenSplit plugin.
"""

from __future__ import annotations

from datetime import date
import json

import greensplit as gs


# Creating Plugin connects this module to GreenSplit. GreenSplit reads
# plugin.toml during discovery, then imports this file only when the component
# is present in the active layout.
plugin = gs.Plugin()


class ResetsTodaySettings(gs.Settings):
    """Settings shown in GreenSplit's component settings panel."""

    label = gs.setting.text(
        "Label",
        default="Resets Today",
        description="Text shown on the left side of the component.",
    )
    value_color = gs.setting.color(
        "Value color",
        default="#ffffffff",
        description="Color used for the reset count.",
    )


def _run_key(run: gs.RunSnapshot) -> str:
    """Return a stable key for the active game and category.

    A file path is not used because users can rename or move a splits file.
    Sorting category variables keeps the key stable when their dictionary
    order changes.
    """

    identity = {
        "game": run.game_name,
        "category": run.category_name,
        "platform": run.platform_name,
        "region": run.region_name,
        "variables": dict(sorted(run.variables.items())),
        "branch": run.branch_id,
    }
    return json.dumps(identity, sort_keys=True, separators=(",", ":"))


# Storage belongs only to this plugin. Assigning a value writes storage.json
# atomically. The host validates that every stored value can be encoded as
# JSON, so use dictionaries, lists, strings, numbers, booleans, and null.
saved = plugin.storage.get("state", {})
if not isinstance(saved, dict):
    saved = {}

raw_counts = saved.get("counts", {})
counts: dict[str, dict[str, int]] = raw_counts if isinstance(raw_counts, dict) else {}

raw_tokens = saved.get("last_reset_token", {})
last_reset_token: dict[str, str] = raw_tokens if isinstance(raw_tokens, dict) else {}


def _persist() -> None:
    """Save a complete new state after an event changes it."""

    plugin.storage["state"] = {
        "counts": counts,
        "last_reset_token": last_reset_token,
    }


@plugin.component("resets_today", settings=ResetsTodaySettings)
def resets_today(
    ctx: gs.RenderContext, settings: ResetsTodaySettings
) -> gs.View:
    """Render one standard information row in the active layout."""

    run_counts = counts.get(_run_key(ctx.run), {})
    value = int(run_counts.get(date.today().isoformat(), 0))
    return gs.ui.info(settings.label, value, value_color=settings.value_color)


@plugin.on_reset
def timer_reset(event: gs.ResetEvent) -> None:
    """Count an unfinished reset once and save it immediately.

    GreenSplit also sends a reset after a completed run. The completed flag
    lets this plugin count only attempts that ended early.
    """

    if event.completed:
        return

    key = _run_key(event.snapshot.run)
    day = date.today().isoformat()

    # The attempt start timestamp identifies the run that was reset. The
    # sequence fallback also gives older hosts a unique token. Remembering the
    # token makes handling idempotent if an event is ever delivered twice.
    token = event.snapshot.timer.attempt_started_at
    if not token:
        token = f"sequence:{event.snapshot.sequence}"
    if last_reset_token.get(key) == token:
        return

    run_counts = counts.setdefault(key, {})
    run_counts[day] = int(run_counts.get(day, 0)) + 1
    last_reset_token[key] = token
    _persist()
