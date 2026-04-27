
import json
import unittest
from unittest.mock import MagicMock, patch
from classifier import SupportClassifier, VALID_CATEGORIES, VALID_PRIORITIES


def make_mock_response(category: str, priority: str):
    """Build a mock OpenAI API response."""
    mock_message = MagicMock()
    mock_message.content = json.dumps({"category": category, "priority": priority})
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


class TestSupportClassifier(unittest.TestCase):

    def setUp(self):
        with patch("classifier.OpenAI"):
            self.clf = SupportClassifier(api_key="test-key")

    # ── Validation ─────────────────────────────────────────────────────────

    def test_valid_categories_and_priorities(self):
        self.assertEqual(VALID_CATEGORIES, {"Billing", "Technical Issue", "Account", "General Inquiry"})
        self.assertEqual(VALID_PRIORITIES, {"High", "Medium", "Low"})

    def test_validate_good_result(self):
        result = self.clf._validate({"category": "Billing", "priority": "High"})
        self.assertEqual(result, {"category": "Billing", "priority": "High"})

    def test_validate_bad_category(self):
        with self.assertRaises(ValueError) as ctx:
            self.clf._validate({"category": "Unknown", "priority": "High"})
        self.assertIn("category", str(ctx.exception))

    def test_validate_bad_priority(self):
        with self.assertRaises(ValueError) as ctx:
            self.clf._validate({"category": "Billing", "priority": "Critical"})
        self.assertIn("priority", str(ctx.exception))

    # ── classify() input guards ─────────────────────────────────────────────

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            self.clf.classify([])

    def test_non_list_raises(self):
        with self.assertRaises(ValueError):
            self.clf.classify("not a list")

    def test_empty_string_message_raises(self):
        with self.assertRaises(ValueError):
            self.clf.classify([""])

    # ── Happy path with mocked API ──────────────────────────────────────────

    def test_classify_billing_high(self):
        self.clf.client.chat.completions.create = MagicMock(
            return_value=make_mock_response("Billing", "High")
        )
        results = self.clf.classify(["My payment got deducted but service is not activated"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "Billing")
        self.assertEqual(results[0]["priority"], "High")

    def test_classify_multiple_messages(self):
        responses = [
            make_mock_response("Billing", "High"),
            make_mock_response("Technical Issue", "Medium"),
            make_mock_response("Account", "Low"),
        ]
        self.clf.client.chat.completions.create = MagicMock(side_effect=responses)
        messages = [
            "My payment got deducted but service is not activated",
            "App crashes every time I login",
            "How to change my email address?",
        ]
        results = self.clf.classify(messages)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["category"], "Billing")
        self.assertEqual(results[1]["category"], "Technical Issue")
        self.assertEqual(results[2]["category"], "Account")

    def test_output_preserves_original_message(self):
        self.clf.client.chat.completions.create = MagicMock(
            return_value=make_mock_response("General Inquiry", "Low")
        )
        msg = "How do I upgrade my plan?"
        results = self.clf.classify([msg])
        self.assertEqual(results[0]["message"], msg)

    def test_output_keys(self):
        self.clf.client.chat.completions.create = MagicMock(
            return_value=make_mock_response("Account", "Medium")
        )
        results = self.clf.classify(["I forgot my password"])
        self.assertIn("message", results[0])
        self.assertIn("category", results[0])
        self.assertIn("priority", results[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
