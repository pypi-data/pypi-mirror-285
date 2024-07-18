import unittest
from json_repair import repair_json
from error_format import *




class TestJsonRepair(unittest.TestCase):
    def test_basic_types_valid(self):
        self.assertEqual(repair_json('{"test": 123}'), {"test": 123})
    def test_lack_of_comma(self):
        self.assertEqual(repair_json(ERROR_FORMAT1), CORRECT_FORMAT1)
    def test_redundant_comma_at_the_end(self):
        self.assertEqual(repair_json(ERROR_FORMAT2), CORRECT_FORMAT2)
    def test_missing_quotation_marks(self):
        self.assertEqual(repair_json(ERROR_FORMAT3), CORRECT_FORMAT3)
    def test_missing_parentheses(self):
        self.assertEqual(repair_json(ERROR_FORMAT4), CORRECT_FORMAT4)
    def test_error_boolean_value(self):
        self.assertEqual(repair_json(ERROR_FORMAT5), CORRECT_FORMAT5)
    def test_error_apostrophe(self):
        self.assertEqual(repair_json(ERROR_FORMAT6), CORRECT_FORMAT6)
    def test_error_none(self):
        self.assertEqual(repair_json(ERROR_FORMAT7), CORRECT_FORMAT7)

class TestExceptions(unittest.TestCase):
    def test_invalid_json(self):
        with self.assertRaises(ValueError) as context: 
            repair_json('hello')
        self.assertEqual(str(context.exception), 'Invalid JSON string')