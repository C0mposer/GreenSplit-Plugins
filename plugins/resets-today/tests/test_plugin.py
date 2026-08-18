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
        self.plugin_id = "com.greensplit.resets-today"
        self.plugin_name = "Resets Today"
        self.plugin_version = "4.0.0"
        self.snapshot = gs.Snapshot()
        self.plugin: gs.Plugin | None = None

    def register_plugin(self, plugin: gs.Plugin) -> None:
        self.plugin = plugin

    def send(self, _payload: Mapping[str, Any]) -> None:
        pass

    def start_task(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        coroutine.close()


def load_component(runtime: FakeRuntime) -> gs.Component:
    spec = importlib.util.spec_from_file_location(
        "resets_today_test_entrypoint", PLUGIN_ROOT / "main.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert runtime.plugin is not None
    component_type = runtime.plugin._components["resets_today"]
    component = component_type()
    component._runtime = runtime
    component._instance_id = "resets-instance"
    return component


class ResetsTodayTests(unittest.TestCase):
    def test_counts_only_unfinished_resets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FakeRuntime(Path(temporary))
            _set_runtime(runtime)
            try:
                component = load_component(runtime)
                component.on_reset(gs.ResetEvent(runtime.snapshot, completed=False))
                component.on_reset(gs.ResetEvent(runtime.snapshot, completed=True))

                context = gs.ComponentContext(
                    component.instance_id,
                    runtime.snapshot.run,
                    runtime.snapshot.timer,
                    runtime.snapshot.analysis,
                )
                self.assertEqual(component.render(context).to_payload(), {
                    "type": "info",
                    "label": "Resets Today",
                    "value": "1",
                })
            finally:
                _set_runtime(None)


if __name__ == "__main__":
    unittest.main()
