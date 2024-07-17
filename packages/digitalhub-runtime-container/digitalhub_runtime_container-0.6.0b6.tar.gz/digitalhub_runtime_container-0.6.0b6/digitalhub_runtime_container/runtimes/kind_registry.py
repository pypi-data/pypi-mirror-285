from __future__ import annotations

from digitalhub_core.runtimes.kind_registry import KindRegistry

kind_registry = KindRegistry(
    {
        "executable": {"kind": "container"},
        "task": [
            {"kind": "container+job", "action": "job"},
            {"kind": "container+serve", "action": "serve"},
            {"kind": "container+build", "action": "build"},
            {"kind": "container+deploy", "action": "deploy"},
        ],
        "run": {"kind": "container+run"},
    }
)
