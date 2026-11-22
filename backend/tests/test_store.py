"""Validation tests for the scheme data file (Slice 1).

Checks data/schemes.json against data/schema.json and the minimum
content rules from PROMPT.md (Slice 1 PROVE section).
Run with: python -m unittest backend.tests.test_store -v
"""
import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SCHEMA_PATH = DATA_DIR / "schema.json"
SCHEMES_PATH = DATA_DIR / "schemes.json"


def _load(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class SchemeDataTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.schema = _load(SCHEMA_PATH)
        cls.schemes = _load(SCHEMES_PATH)
        cls.validator = Draft202012Validator(cls.schema)

    def test_schema_is_a_valid_json_schema(self):
        Draft202012Validator.check_schema(self.schema)

    def test_schemes_file_is_a_non_empty_list(self):
        self.assertIsInstance(self.schemes, list)
        self.assertGreaterEqual(len(self.schemes), 1)

    def test_every_scheme_validates_against_schema(self):
        errors = []
        for scheme in self.schemes:
            sid = scheme.get("id", "<no id>")
            for err in self.validator.iter_errors(scheme):
                errors.append(f"{sid}: {err.message}")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_every_scheme_has_minimum_content(self):
        problems = []
        for scheme in self.schemes:
            sid = scheme.get("id", "<no id>")
            if len(scheme.get("rules", [])) < 2:
                problems.append(f"{sid}: needs at least 2 rules")
            if len(scheme.get("documents", [])) < 1:
                problems.append(f"{sid}: needs at least 1 document")
            if len(scheme.get("apply_steps", [])) < 2:
                problems.append(f"{sid}: needs at least 2 apply steps")
            if not scheme.get("source_url"):
                problems.append(f"{sid}: missing source_url")
            # last_verified may be null only when the scheme is flagged
            # needs_verification (open item, not an invented date).
            if not scheme.get("last_verified") and not scheme.get("needs_verification"):
                problems.append(f"{sid}: needs last_verified or needs_verification")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_no_sensitive_id_or_bank_fields(self):
        # Aadhaar text is allowed inside "documents" lists only, so the raw
        # file check covers account_number and ifsc; keys are checked everywhere.
        text = SCHEMES_PATH.read_text(encoding="utf-8").lower()
        self.assertIsNone(re.search(r"account_number|ifsc", text))

        def iter_keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield key
                    yield from iter_keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from iter_keys(item)

        bad_terms = ("aadhaar", "account", "ifsc", "bank")
        self.assertEqual(
            [k for k in iter_keys(self.schemes) if any(t in k.lower() for t in bad_terms)],
            [],
        )


if __name__ == "__main__":
    unittest.main()
