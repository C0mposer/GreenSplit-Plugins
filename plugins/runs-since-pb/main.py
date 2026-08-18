"""Count runs started since the last personal best."""

import greensplit as gs


plugin = gs.Plugin()


def run_key(run: gs.RunSnapshot):
    return (run.game_name, run.category_name)


@plugin.component(
    "Runs Since PB",
    category="Information",
    description="Shows how many runs you started since your last PB.",
)
class RunsSincePB(gs.Component):
    def __init__(self):
        super().__init__()
        self.counts = {}

    def on_timer_started(self, event: gs.TimerStartedEvent):
        key = run_key(event.run)
        self.counts[key] = self.counts.get(key, 0) + 1

    def on_personal_best(self, event: gs.PersonalBestEvent):
        self.counts[run_key(event.run)] = 0

    def layout(self, ui: gs.UI):
        ui.info("Runs Since PB", self.counts.get(run_key(self.run), 0))
