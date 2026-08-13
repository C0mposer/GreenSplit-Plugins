"""A small GreenSplit plugin that counts runs since the last PB.

This file is intentionally detailed. It is meant to be useful as a starting
point for people writing their first GreenSplit plugin.
"""

from __future__ import annotations

import json

import greensplit as gs


# Creating Plugin connects this module to GreenSplit. GreenSplit reads
# plugin.toml during discovery, then imports this file only when the component
# is present in the active layout.
plugin = gs.Plugin()


class RunsSincePbSettings(gs.Settings):
    """Settings shown in GreenSplit's component settings panel."""

    label = gs.setting.text(
        "Label",
        default="Runs Since PB",
        description="Text shown on the left side of the component.",
    )
    value_color = gs.setting.color(
        "Value color",
        default="#ffffffff",
        description="Color used for the run count.",
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
# atomically. Counts and event tokens are kept in separate dictionaries so the
# same plugin can track several games and categories.
saved = plugin.storage.get("state", {})
if not isinstance(saved, dict):
    saved = {}

raw_counts = saved.get("counts", {})
counts: dict[str, int] = raw_counts if isinstance(raw_counts, dict) else {}

raw_tokens = saved.get("last_start_token", {})
last_start_token: dict[str, str] = raw_tokens if isinstance(raw_tokens, dict) else {}


def _persist() -> None:
    """Save a complete new state after an event changes it."""

    plugin.storage["state"] = {
        "counts": counts,
        "last_start_token": last_start_token,
    }


@plugin.component("runs_since_pb", settings=RunsSincePbSettings)
def runs_since_pb(
    ctx: gs.RenderContext, settings: RunsSincePbSettings
) -> gs.View:
    """Render one standard information row in the active layout."""

    value = int(counts.get(_run_key(ctx.run), 0))
    return gs.ui.info(settings.label, value, value_color=settings.value_color)


@plugin.on_timer_started
def timer_started(event: gs.TimerStartedEvent) -> None:
    """Increment the count when a new attempt begins."""

    key = _run_key(event.snapshot.run)

    # The timestamp identifies this attempt. The sequence fallback also gives
    # older hosts a unique token. Saving the token makes this handler
    # idempotent if an event is ever delivered twice.
    token = event.snapshot.timer.attempt_started_at
    if not token:
        token = f"sequence:{event.snapshot.sequence}"
    if last_start_token.get(key) == token:
        return

    counts[key] = int(counts.get(key, 0)) + 1
    last_start_token[key] = token
    _persist()


@plugin.on_personal_best
def personal_best(event: gs.PersonalBestEvent) -> None:
    """Reset the count only after GreenSplit accepts and saves a PB."""

    key = _run_key(event.snapshot.run)
    if int(counts.get(key, 0)) == 0:
        return

    counts[key] = 0
    _persist()
