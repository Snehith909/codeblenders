"""Slice 2 rules engine tests (CONTEXT.md section 12, T1-T5, plus operator coverage).

Run from the project root with:  python -m unittest discover -s backend/tests
"""
import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
sys.path.insert(0, str(BACKEND_DIR))

import engine  # noqa: E402

PROFILE_FIELDS = [
    "age", "gender", "occupation", "land_acres", "land_ownership",
    "annual_income", "category", "district", "has_bank_account",
    "is_income_tax_payer",
]


def _load_schemes():
    with open(DATA_DIR / "schemes.json", encoding="utf-8") as fh:
        return json.load(fh)


def _pm_kisan():
    for scheme in _load_schemes():
        if scheme["id"] == "pm-kisan":
            return scheme
    raise AssertionError("pm-kisan missing from data/schemes.json")


def _profile(**overrides):
    profile = {field: None for field in PROFILE_FIELDS}
    profile.update(overrides)
    return profile


def _rule(rule_id, field, op, value):
    return {"id": rule_id, "field": field, "op": op, "value": value, "reason": "test rule"}


def _scheme(scheme_id, rules):
    return {"id": scheme_id, "rules": rules}


def _status_for(op, actual, expected):
    """Evaluate one inline rule against one profile value and return the status."""
    scheme = _scheme("inline", [_rule("r1", "x", op, expected)])
    return engine.evaluate({"x": actual}, scheme)["status"]


def _ids(entries):
    return [entry["id"] for entry in entries]


class PmKisanProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scheme = _pm_kisan()

    def test_t1_likely_eligible(self):
        profile = _profile(age=35, occupation="farmer", land_acres=2.0, is_income_tax_payer=False)
        result = engine.evaluate(profile, self.scheme)
        self.assertEqual("pm-kisan", result["scheme_id"])
        self.assertEqual("likely_eligible", result["status"])
        self.assertEqual([], result["failed_rules"])
        self.assertEqual([], result["unknown_rules"])
        self.assertEqual(["r1", "r2"], _ids(result["matched_rules"]))

    def test_t2_tax_payer_not_eligible(self):
        profile = _profile(age=45, occupation="farmer", land_acres=3.0, is_income_tax_payer=True)
        result = engine.evaluate(profile, self.scheme)
        self.assertEqual("not_eligible", result["status"])
        self.assertIn("r2", _ids(result["failed_rules"]))

    def test_t3_land_unknown_maybe(self):
        profile = _profile(age=30, occupation="farmer", land_acres=None, is_income_tax_payer=False)
        result = engine.evaluate(profile, self.scheme)
        self.assertEqual("maybe", result["status"])
        self.assertIn("r1", _ids(result["unknown_rules"]))

    def test_t4_no_land_not_eligible(self):
        profile = _profile(age=28, occupation="farm labourer", land_acres=0, is_income_tax_payer=False)
        result = engine.evaluate(profile, self.scheme)
        self.assertEqual("not_eligible", result["status"])
        self.assertIn("r1", _ids(result["failed_rules"]))

    def test_t4_land_none_is_maybe_not_not_eligible(self):
        profile = _profile(age=28, occupation="farm labourer", land_acres=None, is_income_tax_payer=False)
        result = engine.evaluate(profile, self.scheme)
        self.assertEqual("maybe", result["status"])
        self.assertNotEqual("not_eligible", result["status"])

    def test_t5_all_none_never_likely(self):
        profile = _profile()
        for scheme in _load_schemes():
            with self.subTest(scheme=scheme["id"]):
                result = engine.evaluate(profile, scheme)
                self.assertIn(result["status"], ("maybe", "not_eligible"))
                self.assertNotEqual("likely_eligible", result["status"])

    def test_rule_entries_have_id_field_reason(self):
        profile = _profile(age=35, occupation="farmer", land_acres=2.0, is_income_tax_payer=False)
        result = engine.evaluate(profile, self.scheme)
        for entry in result["matched_rules"]:
            self.assertEqual({"id", "field", "reason"}, set(entry))


class UnknownOperatorTests(unittest.TestCase):
    def test_unknown_operator_marked_unknown_and_logged(self):
        scheme = _scheme("bad-op", [_rule("r1", "land_acres", "between", [0, 5])])
        profile = _profile(land_acres=7.5)
        with self.assertLogs(level="WARNING") as captured:
            result = engine.evaluate(profile, scheme)
        self.assertEqual("maybe", result["status"])
        self.assertIn("r1", _ids(result["unknown_rules"]))
        self.assertEqual([], result["failed_rules"])
        log_text = "\n".join(captured.output)
        self.assertIn("between", log_text)
        self.assertNotIn("7.5", log_text, "warning must not contain profile values")

    def test_apply_op_unknown_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            engine.apply_op("between", 1, 2)
        self.assertIn("Unknown rule operator", str(ctx.exception))


class OperatorTests(unittest.TestCase):
    def test_eq(self):
        self.assertEqual("likely_eligible", _status_for("eq", 5, 5))
        self.assertEqual("not_eligible", _status_for("eq", 5, 6))

    def test_neq(self):
        self.assertEqual("likely_eligible", _status_for("neq", 5, 6))
        self.assertEqual("not_eligible", _status_for("neq", 5, 5))

    def test_gt(self):
        self.assertEqual("likely_eligible", _status_for("gt", 6, 5))
        self.assertEqual("not_eligible", _status_for("gt", 5, 5))

    def test_gte(self):
        self.assertEqual("likely_eligible", _status_for("gte", 5, 5))
        self.assertEqual("not_eligible", _status_for("gte", 4, 5))

    def test_lt(self):
        self.assertEqual("likely_eligible", _status_for("lt", 4, 5))
        self.assertEqual("not_eligible", _status_for("lt", 5, 5))

    def test_lte(self):
        self.assertEqual("likely_eligible", _status_for("lte", 5, 5))
        self.assertEqual("not_eligible", _status_for("lte", 6, 5))

    def test_in(self):
        self.assertEqual("likely_eligible", _status_for("in", "a", ["a", "b"]))
        self.assertEqual("not_eligible", _status_for("in", "c", ["a", "b"]))

    def test_not_in(self):
        self.assertEqual("likely_eligible", _status_for("not_in", "c", ["a", "b"]))
        self.assertEqual("not_eligible", _status_for("not_in", "a", ["a", "b"]))

    def test_exists_pass_and_fail(self):
        self.assertEqual("likely_eligible", _status_for("exists", 1, None))
        # A None value is unknown in evaluate(); the False branch is checked on apply_op.
        self.assertEqual("maybe", _status_for("exists", None, None))
        self.assertTrue(engine.apply_op("exists", 0, None))
        self.assertFalse(engine.apply_op("exists", None, None))

    def test_none_is_unknown_for_every_operator(self):
        for op in ("eq", "neq", "gt", "gte", "lt", "lte", "in", "not_in", "exists"):
            with self.subTest(op=op):
                self.assertEqual("maybe", _status_for(op, None, 1))


class MatchAllTests(unittest.TestCase):
    def test_sorted_likely_maybe_not_eligible_and_stable(self):
        profile = {"x": 1}
        schemes = [
            _scheme("A-not", [_rule("r1", "x", "eq", 2)]),      # not_eligible
            _scheme("B-likely", [_rule("r1", "x", "eq", 1)]),   # likely_eligible
            _scheme("C-maybe", [_rule("r1", "y", "eq", 1)]),    # maybe
            _scheme("D-likely", [_rule("r1", "x", "eq", 1)]),   # likely_eligible
        ]
        results = engine.match_all(profile, schemes)
        self.assertEqual(
            ["B-likely", "D-likely", "C-maybe", "A-not"],
            [r["scheme_id"] for r in results],
        )
        self.assertEqual(
            ["likely_eligible", "likely_eligible", "maybe", "not_eligible"],
            [r["status"] for r in results],
        )


if __name__ == "__main__":
    unittest.main()
