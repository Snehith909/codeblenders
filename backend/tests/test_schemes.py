"""Slice 1 data checks for data/schema.json and data/schemes.json.

Run from the project root with:  python -m unittest discover -s backend/tests
Requires the jsonschema package (pip install jsonschema).
"""
import json
import unittest
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FORBIDDEN_KEY_TERMS = ("aadhaar", "account", "ifsc", "bank")
AADHAAR_DOC_TEXT = "aadhaar"


def _load(name):
    with open(DATA_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


def _require_jsonschema():
    """Import jsonschema or fail loudly (never skip)."""
    try:
        import jsonschema
    except ImportError:
        raise AssertionError(
            "jsonschema is not installed. Install it with: pip install jsonschema "
            "(this test deliberately fails rather than skipping)."
        )
    return jsonschema


def _iter_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _iter_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_keys(item)


def _iter_strings_outside_documents(node):
    """Yield (path_hint, string) for every string value not inside a 'documents' list."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "documents":
                continue
            yield from _iter_strings_outside_documents(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_strings_outside_documents(item)
    elif isinstance(node, str):
        yield node


class SchemeDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = _load("schema.json")
        cls.schemes = _load("schemes.json")

    def test_jsonschema_is_installed(self):
        _require_jsonschema()

    def test_each_scheme_validates_against_schema(self):
        jsonschema = _require_jsonschema()

        validator_cls = jsonschema.validators.validator_for(self.schema)
        validator = validator_cls(self.schema)
        for index, scheme in enumerate(self.schemes):
            with self.subTest(index=index, id=scheme.get("id")):
                errors = sorted(validator.iter_errors(scheme), key=lambda e: list(e.path))
                self.assertEqual(
                    [], [f"{list(e.path)}: {e.message}" for e in errors],
                    "scheme failed schema validation",
                )

    def test_exactly_ten_schemes(self):
        self.assertEqual(10, len(self.schemes))

    def test_ids_are_unique(self):
        ids = [s["id"] for s in self.schemes]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids in {ids}")

    def test_no_forbidden_keys_anywhere(self):
        for key in _iter_keys(self.schemes):
            lowered = key.lower()
            for term in FORBIDDEN_KEY_TERMS:
                self.assertNotIn(term, lowered, f"forbidden key {key!r} in schemes.json")

    def test_aadhaar_text_only_in_documents(self):
        for text in _iter_strings_outside_documents(self.schemes):
            self.assertNotIn(
                AADHAAR_DOC_TEXT,
                text.lower(),
                f"Aadhaar text appears outside a documents list: {text!r}",
            )

    def test_unverified_schemes_are_flagged(self):
        for scheme in self.schemes:
            if scheme["last_verified"] is None:
                self.assertTrue(
                    scheme["needs_verification"],
                    f"{scheme['id']} has last_verified null but needs_verification is not true",
                )


if __name__ == "__main__":
    unittest.main()
