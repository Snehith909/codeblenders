import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extract import FALLBACK, extract_profile  # noqa: E402


def make_fake(responses):
    """Fake post(payload) that returns or raises the given responses in order."""
    calls = []

    def post(payload):
        calls.append(payload)
        response = responses[len(calls) - 1]
        if isinstance(response, Exception):
            raise response
        return response

    post.calls = calls
    return post


VALID_FARMER = (
    '{"age":35,"occupation":"farmer","land_acres":2,"district":"Mandya",'
    '"gender":null,"land_ownership":null,"annual_income":null,"category":null,'
    '"has_bank_account":null,"is_income_tax_payer":null}'
)


class ExtractProfileTest(unittest.TestCase):
    def test_valid_profile_parsed(self):
        post = make_fake([VALID_FARMER])
        result = extract_profile("I am a farmer in Mandya with 2 acres, age 35", post=post)

        self.assertEqual(result["age"], 35)
        self.assertEqual(result["occupation"], "farmer")
        self.assertEqual(result["land_acres"], 2)
        self.assertEqual(result["district"], "Mandya")
        self.assertIn("annual_income", result["missing_fields"])
        self.assertNotIn("age", result["missing_fields"])
        self.assertEqual(len(post.calls), 1)

    def test_invalid_json_twice_returns_fallback(self):
        post = make_fake(["not json", "not json"])
        result = extract_profile("some text", post=post)

        self.assertEqual(result, {"error": "extraction_failed", "fallback": "manual_form"})
        self.assertEqual(len(post.calls), 2)

    def test_invalid_then_valid_returns_profile(self):
        post = make_fake(["not json", VALID_FARMER])
        result = extract_profile("I am a farmer in Mandya with 2 acres, age 35", post=post)

        self.assertEqual(result["age"], 35)
        self.assertEqual(result["district"], "Mandya")
        self.assertEqual(len(post.calls), 2)

    def test_fenced_json_is_accepted(self):
        post = make_fake(["```json\n" + VALID_FARMER + "\n```"])
        result = extract_profile("text", post=post)

        self.assertEqual(result["occupation"], "farmer")
        self.assertEqual(len(post.calls), 1)

    def test_no_api_key_returns_fallback_without_network(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with mock.patch("extract._default_post") as default_post:
                result = extract_profile("I am a farmer in Mandya with 2 acres, age 35")

        self.assertEqual(result, {"error": "extraction_failed", "fallback": "manual_form"})
        default_post.assert_not_called()

    def test_sensitive_keys_and_numbers_are_dropped(self):
        post = make_fake(['{"age":30,"aadhaar":"123456789012","account_number":"5555"}'])
        result = extract_profile("my aadhaar is 123456789012, age 30", post=post)

        self.assertEqual(result["age"], 30)
        for key in result:
            self.assertNotIn("aadhaar", key.lower())
            if key != "has_bank_account":
                self.assertNotIn("account", key.lower())
        self.assertNotIn("account_number", result)
        self.assertNotIn("123456789012", str(result))
        self.assertNotIn("5555", str(result))

    def test_post_raising_twice_returns_fallback(self):
        post = make_fake([RuntimeError("boom"), RuntimeError("boom again")])
        result = extract_profile("text", post=post)

        self.assertEqual(result, {"error": "extraction_failed", "fallback": "manual_form"})
        self.assertEqual(len(post.calls), 2)


if __name__ == "__main__":
    unittest.main()
