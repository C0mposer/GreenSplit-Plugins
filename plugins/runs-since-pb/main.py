"""Count runs started since the last personal best."""

import greensplit as gs


plugin = gs.Plugin()
run_counts: dict[tuple[str, str], int] = {}


def run_key(run: gs.RunSnapshot) -> tuple[str, str]:
    return run.game_name, run.category_name


@plugin.layout_component("runs_since_pb")
def render(ctx: gs.ComponentContext) -> gs.Element:
    return gs.ui.label_value("Runs Since PB", run_counts.get(run_key(ctx.run), 0))


@plugin.on_timer_started
def count_run(event: gs.TimerStartedEvent) -> None:
    key = run_key(event.snapshot.run)
    run_counts[key] = run_counts.get(key, 0) + 1


@plugin.on_personal_best
def reset_count(event: gs.PersonalBestEvent) -> None:
    run_counts[run_key(event.snapshot.run)] = 0
