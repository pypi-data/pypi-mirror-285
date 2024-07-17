from __future__ import annotations

from digitalhub_core.runtimes.kind_registry import KindRegistry

kind_registry = KindRegistry(
    {
        "executable": {"kind": "nefertem"},
        "task": [
            {"kind": "nefertem+infer", "action": "infer"},
            {"kind": "nefertem+profile", "action": "profile"},
            {"kind": "nefertem+validate", "action": "validate"},
        ],
        "run": {"kind": "nefertem+run"},
    }
)
