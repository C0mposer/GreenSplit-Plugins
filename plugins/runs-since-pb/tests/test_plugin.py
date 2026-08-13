from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
from typing import Any, Coroutine, Mapping
import unittest

import greensplit as gs
from greensplit.plugin import _set_runtime


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class FakeRuntime:
    """Provide the narrow runtime protocol used by the real plugin worker."""

    def __init__(self, data_root: Path) -> None:
        self.plugin_root = PLUGIN_ROOT
        self.data_root = data_root
        self.plugin_id = "com.greensplit.runs-since-pb"
        self.plugin_name = "Runs Since PB"
        self.plugin_version = "1.0.0"
        self.snapshot = gs.Snapshot()
        self.messages: list[dict[str, Any]] = []
        self.plugin: gs.Plugin | None = None

    def register_plugin(self, plugin: gs.Plugin) -> None:
        self.plugin = plugin

    def send(self, payload: Mapping[str, Any]) -> None:
        self.messages.append(dict(payload))

    def start_task(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        coroutine.close()


def snapshot(started_at: str, sequence: int = 1) -> gs.Snapshot:
    return gs.Snapshot(
        sequence=sequence,
        run=gs.RunSnapshot(game_name="Example Game", category_name="Any%"),
        timer=gs.TimerSnapshot(attempt_started_at=started_at),
    )


class RunsSincePbTests(unittest.TestCase):
    def test_counts_starts_once_then_resets_after_a_pb(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FakeRuntime(Path(temporary))
            runtime.snapshot = snapshot("2026-08-13T07:00:00.000Z")
            _set_runtime(runtime)
            try:
                spec = importlib.util.spec_from_file_location(
                    "runs_since_pb_test_entrypoint", PLUGIN_ROOT / "main.py"
                )
                assert spec is not None and spec.loader is not None
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert runtime.plugin is not None

                started = gs.TimerStartedEvent(runtime.snapshot)
                for callback in runtime.plugin._handlers[type(started)]:
                    callback(started)
                    callback(started)

                context = gs.RenderContext(
                    "runs-instance",
                    runtime.snapshot.run,
                    runtime.snapshot.timer,
                    runtime.snapshot.analysis,
                )
                component = runtime.plugin._components["runs_since_pb"]
                settings = module.RunsSincePbSettings()
                before_pb = component(context, settings).to_payload()
                self.assertEqual(before_pb["value"], "1")
                self.assertEqual(before_pb["value_color"], "#ffffffff")

                pb = gs.PersonalBestEvent(runtime.snapshot)
                for callback in runtime.plugin._handlers[type(pb)]:
                    callback(pb)

                after_pb = component(context, settings).to_payload()
                self.assertEqual(after_pb["value"], "0")

                stored = json.loads(
                    (Path(temporary) / "storage.json").read_text(encoding="utf-8")
                )
                self.assertIn("state", stored)
            finally:
                _set_runtime(None)


if __name__ == "__main__":
    unittest.main()
