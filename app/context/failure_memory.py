"""
Failure Memory — tracks validation failures per (use_case, audience_id).

Enables failure-aware generation: the repair prompt and subsequent generation
prompts inject what failed last time, preventing the same failure patterns.

Thread-safe singleton. Max 10 failures tracked per context key.
"""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class FailureRecord:
    timestamp: str
    validator_issues: list[str]       # From quality validator
    humanization_issues: list[str]    # From humanization validator
    platform_violations: list[str]    # From platform.validate_output()
    banned_phrases_found: list[str]   # Banned phrases detected in output
    score: int = 0                    # Humanization score at time of failure
    repaired: bool = False

    def to_context_block(self) -> str:
        lines = ["PREVIOUS ATTEMPT FAILURES (avoid repeating these):"]
        if self.validator_issues:
            lines.append("  Quality issues: " + " | ".join(self.validator_issues[:3]))
        if self.humanization_issues:
            lines.append("  Humanization issues: " + " | ".join(self.humanization_issues[:3]))
        if self.platform_violations:
            lines.append("  Platform violations: " + " | ".join(self.platform_violations[:2]))
        if self.banned_phrases_found:
            sample = self.banned_phrases_found[:4]
            lines.append('  Banned phrases used: ' + ", ".join(f'"{p}"' for p in sample))
        return "\n".join(lines)


class FailureMemory:
    """
    Thread-safe per-context failure store.
    Key: (use_case, audience_id) → deque of FailureRecord
    """

    def __init__(self, max_per_context: int = 10) -> None:
        self._store: dict[str, deque[FailureRecord]] = defaultdict(
            lambda: deque(maxlen=max_per_context)
        )
        self._lock = threading.Lock()

    def _key(self, use_case: str, audience_id: str) -> str:
        return f"{use_case.lower().strip()}::{audience_id.lower().strip()}"

    def record(
        self,
        use_case: str,
        audience_id: str,
        validator_issues: list[str],
        humanization_issues: list[str],
        platform_violations: list[str],
        banned_phrases_found: list[str],
        score: int = 0,
        repaired: bool = False,
    ) -> None:
        record = FailureRecord(
            timestamp=datetime.utcnow().isoformat(),
            validator_issues=validator_issues,
            humanization_issues=humanization_issues,
            platform_violations=platform_violations,
            banned_phrases_found=banned_phrases_found,
            score=score,
            repaired=repaired,
        )
        key = self._key(use_case, audience_id)
        with self._lock:
            self._store[key].append(record)

    def get_recent(
        self,
        use_case: str,
        audience_id: str,
        n: int = 3,
    ) -> list[FailureRecord]:
        key = self._key(use_case, audience_id)
        with self._lock:
            records = list(self._store.get(key, deque()))
        return records[-n:]

    def get_failure_context(
        self,
        use_case: str,
        audience_id: str,
        n: int = 2,
    ) -> Optional[str]:
        """
        Return a compact failure context block for prompt injection.
        Returns None if no failures recorded for this context.
        """
        recent = self.get_recent(use_case, audience_id, n)
        if not recent:
            return None

        # Aggregate issues across recent failures
        all_validator: list[str] = []
        all_human: list[str] = []
        all_platform: list[str] = []
        all_banned: list[str] = []

        for r in recent:
            all_validator.extend(r.validator_issues)
            all_human.extend(r.humanization_issues)
            all_platform.extend(r.platform_violations)
            all_banned.extend(r.banned_phrases_found)

        # Deduplicate, preserve order
        def dedup(lst: list[str]) -> list[str]:
            return list(dict.fromkeys(lst))

        synthetic = FailureRecord(
            timestamp=recent[-1].timestamp,
            validator_issues=dedup(all_validator)[:4],
            humanization_issues=dedup(all_human)[:4],
            platform_violations=dedup(all_platform)[:3],
            banned_phrases_found=dedup(all_banned)[:5],
            score=recent[-1].score,
        )

        if not any([
            synthetic.validator_issues,
            synthetic.humanization_issues,
            synthetic.platform_violations,
            synthetic.banned_phrases_found,
        ]):
            return None

        return synthetic.to_context_block()

    def clear(self, use_case: str = "", audience_id: str = "") -> None:
        with self._lock:
            if use_case or audience_id:
                key = self._key(use_case, audience_id)
                self._store.pop(key, None)
            else:
                self._store.clear()

    def stats(self) -> dict:
        with self._lock:
            return {
                "contexts_tracked": len(self._store),
                "total_failures": sum(len(v) for v in self._store.values()),
            }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_memory = FailureMemory()


def record(
    use_case: str,
    audience_id: str,
    validator_issues: list[str],
    humanization_issues: list[str],
    platform_violations: list[str],
    banned_phrases_found: list[str],
    score: int = 0,
    repaired: bool = False,
) -> None:
    _memory.record(
        use_case, audience_id,
        validator_issues, humanization_issues,
        platform_violations, banned_phrases_found,
        score, repaired,
    )


def get_failure_context(use_case: str, audience_id: str, n: int = 2) -> Optional[str]:
    return _memory.get_failure_context(use_case, audience_id, n)


def get_recent(use_case: str, audience_id: str, n: int = 3) -> list[FailureRecord]:
    return _memory.get_recent(use_case, audience_id, n)


def clear(use_case: str = "", audience_id: str = "") -> None:
    _memory.clear(use_case, audience_id)


def stats() -> dict:
    return _memory.stats()
