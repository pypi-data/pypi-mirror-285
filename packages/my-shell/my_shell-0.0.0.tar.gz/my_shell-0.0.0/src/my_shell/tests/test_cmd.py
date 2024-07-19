import unittest

from ..cmd import matches


class TestMatches(unittest.TestCase):
    def test_both_empty(self):
        result, subs = matches(alias=[], pattern=[])
        self.assertTrue(result)
        self.assertEqual(subs, dict())

    def test_star_with_empty_command(self):
        result, subs = matches(alias=[], pattern=["*"])
        self.assertTrue(result)
        self.assertEqual(subs, dict())

    def test_star_with_single_command(self):
        result, subs = matches(alias=["a"], pattern=["*"])
        self.assertTrue(result)
        self.assertEqual(subs, dict())

    def test_star_with_multiple_command(self):
        result, subs = matches(alias=["a", "b"], pattern=["*"])
        self.assertTrue(result)
        self.assertEqual(subs, dict())

    def test_star_with_empty_pattern(self):
        result, subs = matches(alias=["a"], pattern=[])
        self.assertFalse(result)
        self.assertEqual(subs, dict())

    def test_simple_optinal_subs_when_they_match(self):
        result, subs = matches(alias=["value"], pattern=["?key?[value]"])
        self.assertTrue(result)
        self.assertEqual(subs, {"key": "value"})

    def test_simple_optional_subs_when_they_dont_match(self):
        result, subs = matches(alias=["not_a_value"], pattern=["?key?[value]"])
        self.assertFalse(result)
        self.assertEqual(subs, dict())

    def test_simple_optional_subs_when_they_dont_match_with_star(self):
        result, subs = matches(alias=["not_a_value"], pattern=["?key?[value]", "*"])
        self.assertTrue(result)
        self.assertEqual(subs, dict())

    def test_simple_mandatory_subs_when_the_match(self):
        result, subs = matches(alias=["value"], pattern=["key[value]"])
        self.assertTrue(result)
        self.assertEqual(subs, {"key": "value"})

    def test_simple_mandatory_subs_when_they_dont_match(self):
        result, subs = matches(alias=["not_a_value"], pattern=["key[value]"])
        self.assertFalse(result)
        self.assertEqual(subs, dict())

    def test_simple_mandatory_subs_when_they_dont_match_with_star(self):
        result, subs = matches(alias=["not_a_value"], pattern=["key[value]"])
        self.assertFalse(result)
        self.assertEqual(subs, dict())

    def test_regex_subs_when_they_match(self):
        result, subs = matches(alias=["value"], pattern=["key[.*]"])
        self.assertTrue(result)
        self.assertEqual(subs, {"key": "value"})

    def test_regex_subs_when_they_dont_match(self):
        result, subs = matches(alias=["not_numbers"], pattern=["key[\\d*]"])
        self.assertFalse(result)
        self.assertEqual(subs, dict())


if __name__ == "__main__":
    unittest.main()
