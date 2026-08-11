import greensplit as gs


plugin = gs.Plugin()


@plugin.component("current_segment")
def current_segment(ctx: gs.RenderContext) -> gs.View:
    segment = ctx.timer.current_segment
    return gs.ui.info("Current Segment", segment.name if segment else "—")
