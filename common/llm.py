"""One model-call function with a disk cache, shared by the three pilots.

``call(model, system, user)`` returns the model's text.

- ``cli:<name>`` runs the Claude Code CLI in print mode as a bare model (system
  prompt replaced, tools off). At most ``CLI_SLOTS`` such processes run at once
  across every process on this machine (file locks), because each one is a
  Node process and the laptop has little free memory.
- anything else is a LiteLLM model string (``gemini/...``). Keys come from the
  environment, or from a ``.env`` file at the repository root (git-ignored), or
  from the file named in ``SPRINT_ENV``. They are never printed.

Every call is cached by (model, system, user, max_tokens, temperature, tag) in a
JSONL file, so reruns are free and results are reproducible.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import random
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ENV_FILE = Path(os.environ.get("SPRINT_ENV", Path(__file__).resolve().parent.parent / ".env"))
CLI_SLOTS = int(os.environ.get("CLI_SLOTS", "2"))
SLOT_DIR = Path(tempfile.gettempdir()) / "epistemics-sprint-cli-slots"

_lock = threading.Lock()
_caches: dict[Path, dict[str, str]] = {}
_env_loaded = False


def _load_env() -> None:
    global _env_loaded
    if not _env_loaded and ENV_FILE.exists():
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE)
    _env_loaded = True


def _cache(path: Path) -> dict[str, str]:
    if path not in _caches:
        d: dict[str, str] = {}
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    rec = json.loads(line)
                    d[rec["key"]] = rec["text"]
        _caches[path] = d
    return _caches[path]


def _cli(model: str, system: str, user: str) -> str:
    SLOT_DIR.mkdir(exist_ok=True)
    while True:
        for i in range(CLI_SLOTS):
            f = open(SLOT_DIR / f"slot{i}", "w")  # noqa: SIM115 - held as a lock across the call, closed in finally
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                f.close()
                continue
            try:
                with tempfile.TemporaryDirectory() as cwd:  # no project CLAUDE.md in reach
                    r = subprocess.run(
                        ["claude", "-p", "--model", model, "--system-prompt", system, "--tools", "",
                         "--no-session-persistence", "--strict-mcp-config", "--setting-sources", ""],
                        input=user, capture_output=True, text=True, timeout=300, cwd=cwd, check=False,
                    )
                if r.returncode != 0:
                    raise RuntimeError(r.stderr[-300:] or r.stdout[-300:])
                return r.stdout
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
                f.close()
        time.sleep(0.5 + random.random())


def _litellm(model: str, system: str, user: str, max_tokens: int, temperature: float) -> str:
    import litellm

    litellm.suppress_debug_info = True
    litellm.drop_params = True  # some Gemini models reject temperature
    _load_env()
    delay = 15.0
    for attempt in range(8):
        try:
            r = litellm.completion(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=temperature, max_tokens=max_tokens,
            )
            return r.choices[0].message.content or ""
        except Exception as e:  # rate limits and transient server errors: wait and retry
            name = type(e).__name__
            transient = any(s in name for s in ("RateLimit", "Timeout", "ServiceUnavailable", "InternalServer", "APIConnection"))
            # Gemini's per-minute quota can surface as BadRequestError
            quota = any(s in str(e) for s in ("RESOURCE_EXHAUSTED", "quota", "429"))
            if attempt == 7 or not (transient or quota):
                raise
            time.sleep(delay + random.random() * 5)
            delay = min(delay * 1.6, 90)
    raise RuntimeError("unreachable")


def call(model: str, system: str, user: str, *, max_tokens: int = 700, temperature: float = 0.0,
         tag: str = "", cache: str | Path = ".cache/calls.jsonl") -> str:
    """Return the model's reply text. ``tag`` separates repeated samples of the same prompt."""
    path = Path(cache)
    key = hashlib.sha256(json.dumps([model, system, user, max_tokens, temperature, tag]).encode()).hexdigest()
    with _lock:
        hit = _cache(path).get(key)
    if hit is not None:
        return hit
    if model.startswith("cli:"):
        text = _cli(model[4:], system, user)
    else:
        text = _litellm(model, system, user, max_tokens, temperature)
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        _cache(path)[key] = text
        with path.open("a") as f:
            f.write(json.dumps({"key": key, "model": model, "text": text}) + "\n")
    return text
