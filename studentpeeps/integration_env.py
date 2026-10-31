"""Sandbox vs production integration settings from .env."""

from decouple import config

SANDBOX_ALIASES = frozenset({"sandbox", "test", "staging"})
PRODUCTION_ALIASES = frozenset({"production", "prod", "live"})

WOOHOO_BASE_URL_BY_ENV = {
    "sandbox": "https://sandbox.woohoo.in",
    "production": "https://extapi12.woohoo.in",
}


def normalize_integration_env(raw: str, *, default: str = "production") -> str:
    value = (raw or default).strip().lower()
    if value in SANDBOX_ALIASES:
        return "sandbox"
    if value in PRODUCTION_ALIASES:
        return "production"
    raise ValueError(
        f"Invalid integration environment {raw!r}; use sandbox or production."
    )


def resolve_integration_env(env_var: str, *, legacy_test_flag: bool | None = None) -> str:
    """
    Read ``<PREFIX>_ENV`` from .env, or infer from a legacy boolean test flag
    (e.g. PAYU_USE_TEST) when ``_ENV`` is unset.
    """
    explicit = config(env_var, default="").strip()
    if explicit:
        return normalize_integration_env(explicit)
    if legacy_test_flag is not None:
        return "sandbox" if legacy_test_flag else "production"
    return "production"


