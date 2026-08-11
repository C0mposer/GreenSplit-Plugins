import greensplit as gs


plugin = gs.Plugin()


@plugin.component("run_progress")
def run_progress(ctx: gs.RenderContext) -> gs.View:
    total = max(1, len(ctx.run.segments))
    if ctx.timer.phase is gs.TimerPhase.ENDED:
        completed = total
    else:
        completed = max(0, ctx.timer.current_segment_index or 0)
    return gs.ui.column(
        gs.ui.info("Run Progress", f"{completed} / {total}"),
        gs.ui.progress(completed / total, color="#ff2daf5f"),
        spacing=3.0,
    )
