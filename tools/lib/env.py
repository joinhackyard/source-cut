"""Load <repo>/.env into os.environ (without overriding what the shell already set)."""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.split(" #")[0].strip())
    return os.environ


def need(*keys):
    env = load()
    missing = [k for k in keys if not env.get(k)]
    if missing:
        raise SystemExit(f"set {', '.join(missing)} in .env (see .env.example)")
    return env
