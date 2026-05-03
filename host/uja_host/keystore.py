"""Demoted per ADR-002 D3.

OS keychain wrapper. No longer load-bearing in v0.2.x (Pivot C — Cowork
holds the user's auth, not a per-user Anthropic API key). Kept in case a
future tool needs a credential store (e.g. headless export mode per
ADR-002 §Phasing impact / v0.3.0 reframings). Not part of the default
MCP tool surface.

OS keychain wrapper for the Anthropic API key.

Per ADR-001 §D8:
- Service name:  com.ultimatejobassistant.uja
- Key name:      anthropic_api_key
- Stored via Python's `keyring` library (macOS Keychain, Windows Credential
  Manager, libsecret on Linux).
- The DB stores only a pointer to the keychain entry (service + key_name),
  never the secret itself.
- The key is never logged. `redact_secrets(text)` strips any sk-ant-* token
  from arbitrary text before logging.

Headless / CI fallback:
- If `keyring` raises NoKeyringError (common in containers), we fall back
  to an in-process memory store. THIS IS NOT PERSISTENT and is intended
  only for tests / CI smoke. A clear log line is emitted so users notice.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import keyring
from keyring.errors import KeyringError, NoKeyringError

log = logging.getLogger(__name__)

SERVICE = "com.ultimatejobassistant.uja"
KEY_NAME = "anthropic_api_key"

_SECRET_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]+")

# Memory fallback for headless environments (tests, CI).
_memory_store: dict[str, str] = {}
_using_memory = False


def _set(service: str, key_name: str, value: str) -> None:
    global _using_memory
    try:
        keyring.set_password(service, key_name, value)
    except (NoKeyringError, KeyringError) as exc:
        log.warning(
            "OS keychain unavailable (%s); falling back to in-memory store. "
            "Secret WILL NOT persist across server restart.",
            type(exc).__name__,
        )
        _memory_store[f"{service}:{key_name}"] = value
        _using_memory = True


def _get(service: str, key_name: str) -> Optional[str]:
    if _using_memory:
        return _memory_store.get(f"{service}:{key_name}")
    try:
        return keyring.get_password(service, key_name)
    except (NoKeyringError, KeyringError) as exc:
        log.warning("OS keychain unavailable (%s); checking memory store", type(exc).__name__)
        return _memory_store.get(f"{service}:{key_name}")


def _delete(service: str, key_name: str) -> None:
    if _using_memory:
        _memory_store.pop(f"{service}:{key_name}", None)
        return
    try:
        keyring.delete_password(service, key_name)
    except (NoKeyringError, KeyringError):
        _memory_store.pop(f"{service}:{key_name}", None)


def set_api_key(value: str) -> None:
    if not value or not value.startswith("sk-ant-"):
        raise ValueError("API key does not look like a valid Anthropic key (sk-ant-...)")
    _set(SERVICE, KEY_NAME, value)


def get_api_key() -> Optional[str]:
    return _get(SERVICE, KEY_NAME)


def has_api_key() -> bool:
    val = get_api_key()
    return bool(val)


def clear_api_key() -> None:
    _delete(SERVICE, KEY_NAME)


def redact_secrets(text: str) -> str:
    """Replace every sk-ant-* match with `sk-ant-***REDACTED***`."""
    return _SECRET_RE.sub("sk-ant-***REDACTED***", text)


def using_memory_fallback() -> bool:
    """For diagnostics: returns True if we couldn't reach the OS keychain."""
    return _using_memory
