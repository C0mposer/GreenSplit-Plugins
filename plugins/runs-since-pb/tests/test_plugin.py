from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
from typing import Any, Coroutine, Mapping
import unittest

import greensplit as gs
from greensplit.plugin import _set_runtime


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class FakeRuntime:
    def __init__(self, data_root: Path) -> None:
        self.plugin_root = PLUGIN_ROOT
        self.data_root = data_root
        self.plugin_id = "com.greensplit.runs-since-pb"
        self.plugin_name = "Runs Since PB"
        self.plugin_version = "2.0.0"
        self.snapshot = gs.Snapshot()
        self.plugin: gs.Plugin | None = None

    def register_plugin(self, plugin: gs.Plugin) -> None:
        self.plugin = plugin

    def send(self, _payload: Mapping[str, Any]) -> None:
        pass

    def start_task(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        coroutine.close()


class RunsSincePbTests(unittest.TestCase):
    def test_counts_starts_then_resets_after_a_pb(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FakeRuntime(Path(temporary))
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

                context = gs.ComponentContext(
                    "runs-instance",
                    runtime.snapshot.run,
                    runtime.snapshot.timer,
                    runtime.snapshot.analysis,
                )
                component = runtime.plugin._components["runs_since_pb"]
                self.assertEqual(component(context).to_payload()["value"], "1")

                personal_best = gs.PersonalBestEvent(runtime.snapshot)
                for callback in runtime.plugin._handlers[type(personal_best)]:
                    callback(personal_best)

                self.assertEqual(component(context).to_payload()["value"], "0")
            finally:
                _set_runtime(None)


if __name__ == "__main__":
    unittest.main()
