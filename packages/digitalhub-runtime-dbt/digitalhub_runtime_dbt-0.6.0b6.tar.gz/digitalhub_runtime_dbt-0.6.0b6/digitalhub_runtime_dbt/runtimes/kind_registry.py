from __future__ import annotations

from digitalhub_core.runtimes.kind_registry import KindRegistry

kind_registry = KindRegistry(
    {
        "executable": {"kind": "dbt"},
        "task": [{"kind": "dbt+transform", "action": "transform"}],
        "run": {"kind": "dbt+run"},
    }
)
