"""Count runs started since the last personal best."""

import greensplit as gs


plugin = gs.Plugin()
run_counts = {}


def run_key(run: gs.RunSnapshot):
    game_name = run.game_name
    category_name = run.category_name
    return (game_name, category_name)


@plugin.layout_component(
    name="Runs Since PB",
    category="Information",
    description="Shows how many runs you started since your last PB.",
)
def runs_since_pb(ctx: gs.ComponentContext) -> gs.Element:
    key = run_key(ctx.run)
    count = run_counts.get(key, 0)
    return gs.ui.label_value("Runs Since PB", count)


@plugin.on_timer_started
def count_run(event: gs.TimerStartedEvent) -> None:
    key = run_key(event.snapshot.run)
    old_count = run_counts.get(key, 0)
    run_counts[key] = old_count + 1


@plugin.on_personal_best
def reset_count(event: gs.PersonalBestEvent) -> None:
    key = run_key(event.snapshot.run)
    run_counts[key] = 0
