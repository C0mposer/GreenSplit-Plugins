# GreenSplit Plugins

This repository contains official plugins for the GreenSplit speedrun timer.
The application reads `plugins.json` to display plugins in its store.

## Plugins

- **Resets Today** shows how many runs you reset today.
- **Runs Since PB** shows how many runs you started since your last PB.
- **Number of Paces** counts completed attempts at or below a time you choose.

All three plugins are small reference projects. Their Python files use the
simple `gs.Component` API and keep the examples intentionally easy to read.

Each plugin directory contains its source, documentation, tests, changelog,
and license. Release archives are built by `tools/package_plugins.py`.
