# GreenSplit Plugins

This public registry powers GreenSplit's plugin browser. `plugins.json` is the
single catalog downloaded by the application when the Plugins window opens.

The initial entries are small, real Python components maintained by GreenSplit.
They exist to exercise installation, discovery, and component-only execution
without pretending to be production plugins.

For a real entry, `plugin.toml` remains the source of its package metadata. The
registry adds distribution information, GreenSplit's trust classification, and
the download URL. Entries may declare a `github_release` object containing a
repository, tag, and ZIP asset pattern. The scheduled workflow then refreshes
their cumulative GitHub release-asset download counts without making every
GreenSplit client query the GitHub API.
