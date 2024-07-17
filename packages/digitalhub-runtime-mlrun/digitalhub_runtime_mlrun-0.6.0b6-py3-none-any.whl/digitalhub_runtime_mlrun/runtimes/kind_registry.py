from __future__ import annotations

from digitalhub_core.runtimes.kind_registry import KindRegistry

kind_registry = KindRegistry(
    {
        "executable": {"kind": "mlrun"},
        "task": [
            {"kind": "mlrun+job", "action": "job"},
            {"kind": "mlrun+build", "action": "build"},
        ],
        "run": {"kind": "mlrun+run"},
    }
)
