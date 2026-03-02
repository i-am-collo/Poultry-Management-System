import compileall
import os
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def check_secret_key() -> tuple[bool, str]:
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    secret_key = os.getenv("SECRET_KEY", "").strip()

    if app_env in {"production", "staging"} and not secret_key:
        return False, "SECRET_KEY is required when APP_ENV is production/staging."

    return True, "SECRET_KEY check passed."


def check_python_modules() -> tuple[bool, str]:
    try:
        import app.main  # noqa: F401
    except Exception as exc:  # pragma: no cover
        return False, f"Failed to import app.main: {exc}"
    return True, "Import check passed."


def check_compile() -> tuple[bool, str]:
    ok = compileall.compile_dir("app", quiet=1)
    if not ok:
        return False, "Compile check failed."
    return True, "Compile check passed."


def main() -> int:
    checks = [check_secret_key, check_python_modules, check_compile]
    failed = False

    for check in checks:
        ok, message = check()
        prefix = "OK" if ok else "FAIL"
        print(f"[{prefix}] {message}")
        if not ok:
            failed = True

    if failed:
        print("Preflight failed.")
        return 1

    print("Preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
