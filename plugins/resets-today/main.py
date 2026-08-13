"""Count unfinished resets made today."""

from datetime import date

import greensplit as gs


plugin = gs.Plugin()
reset_counts: dict[tuple[str, str, date], int] = {}


def run_key(run: gs.RunSnapshot) -> tuple[str, str, date]:
    return run.game_name, run.category_name, date.today()


@plugin.layout_component("resets_today")
def render(ctx: gs.ComponentContext) -> gs.Element:
    return gs.ui.label_value("Resets Today", reset_counts.get(run_key(ctx.run), 0))


@plugin.on_reset
def count_reset(event: gs.ResetEvent) -> None:
    if not event.completed:
        key = run_key(event.snapshot.run)
        reset_counts[key] = reset_counts.get(key, 0) + 1
