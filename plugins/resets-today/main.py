"""Count unfinished resets made today."""

from datetime import date

import greensplit as gs


plugin = gs.Plugin()


def run_key(run: gs.RunSnapshot):
    return (run.game_name, run.category_name, date.today())


@plugin.component(
    "Resets Today",
    category="Information",
    description="Shows how many runs you reset today.",
)
class ResetsToday(gs.Component):
    def __init__(self):
        super().__init__()
        self.counts = {}

    def on_reset(self, event: gs.ResetEvent):
        if not event.completed:
            key = run_key(event.run)
            self.counts[key] = self.counts.get(key, 0) + 1

    def layout(self, ui: gs.UI):
        ui.info("Resets Today", self.counts.get(run_key(self.run), 0))
