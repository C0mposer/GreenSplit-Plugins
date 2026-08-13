"""Count unfinished resets made today."""

from datetime import date

import greensplit as gs


plugin = gs.Plugin()
reset_counts = {}


def run_key(run: gs.RunSnapshot):
    game_name = run.game_name
    category_name = run.category_name
    today = date.today()
    return (game_name, category_name, today)


@plugin.layout_component(
    name="Resets Today",
    category="Information",
    description="Shows how many runs you reset today.",
)
def resets_today(ctx: gs.ComponentContext) -> gs.Element:
    key = run_key(ctx.run)
    count = reset_counts.get(key, 0)
    return gs.ui.label_value("Resets Today", count)


@plugin.on_reset
def count_reset(event: gs.ResetEvent) -> None:
    if event.completed is False:
        key = run_key(event.snapshot.run)
        old_count = reset_counts.get(key, 0)
        reset_counts[key] = old_count + 1
