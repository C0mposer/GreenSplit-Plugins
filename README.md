# GreenSplit Plugins

This repository contains official plugins for the GreenSplit speedrun timer.
The application reads `plugins.json` to display plugins in its store.

## Plugins

- **Resets Today** shows how many runs you reset today.
- **Runs Since PB** shows how many runs you started since your last PB.

Both plugins are small reference projects. Their Python files explain the
manifest, settings, events, snapshots, views, and persistent storage used by a
GreenSplit plugin.

Each plugin directory contains its source, documentation, tests, changelog,
and license. Release archives are built by `tools/package_plugins.py`.
