import greensplit as gs


plugin = gs.Plugin()


@plugin.component("attempt_counter")
def attempt_counter(ctx: gs.RenderContext) -> gs.View:
    return gs.ui.info("Attempts", ctx.run.attempt_count)
