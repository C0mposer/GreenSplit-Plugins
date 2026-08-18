"""Count completed attempts at or below a chosen time."""

import greensplit as gs


plugin = gs.Plugin()


@plugin.component(
    "Number of Paces",
    category="Information",
    description="Shows how many completed attempts are at or below a chosen time.",
)
class NumberOfPaces(gs.Component):
    def settings(self, page: gs.SettingsPage):
        page.text("threshold", "Time or better", default="1:30:00")

    def layout(self, ui: gs.UI):
        target = gs.time.parse(self.options.threshold)
        count = sum(
            1
            for attempt in self.run.attempts
            if attempt.finished_time is not None and attempt.finished_time <= target
        )
        ui.info("Number of Paces", count)
