"""Scheme store: load, validate and atomically save data/schemes.json."""
import json
import os
import tempfile
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCHEMES_PATH = DATA_DIR / "schemes.json"
SCHEMA_PATH = DATA_DIR / "schema.json"


def _validate(schemes):
    """Raise ValueError with a plain message if the list is not valid."""
    import jsonschema

    if not isinstance(schemes, list):
        raise ValueError("Schemes must be a list")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    seen_ids = set()
    for index, scheme in enumerate(schemes):
        errors = sorted(validator.iter_errors(scheme), key=lambda e: list(e.path))
        if errors:
            first = errors[0]
            location = ".".join(str(part) for part in first.path) or "scheme"
            raise ValueError(f"Scheme {index} is invalid at {location}: {first.message}")
        scheme_id = scheme["id"]
        if scheme_id in seen_ids:
            raise ValueError(f"Duplicate scheme id: {scheme_id}")
        seen_ids.add(scheme_id)


def load_schemes():
    """Read and validate data/schemes.json. Returns the list of schemes."""
    try:
        schemes = json.loads(SCHEMES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"schemes.json is not valid JSON: {exc.msg}") from exc
    _validate(schemes)
    return schemes


def get_scheme(scheme_id):
    """Return the scheme with this id, or None."""
    for scheme in load_schemes():
        if scheme["id"] == scheme_id:
            return scheme
    return None


def save_schemes(schemes):
    """Validate the whole list, then replace data/schemes.json atomically."""
    _validate(schemes)

    fd, tmp_name = tempfile.mkstemp(dir=DATA_DIR, prefix=".schemes-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(schemes, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, SCHEMES_PATH)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
