import unittest

from ledes_parser.ledes_parser import get_parser


class TestLedes98BParser(unittest.TestCase):
    def setUp(self):
        self.parser = get_parser(spec="98B")

    def test_parse_valid_data(self):
        data = """
LEDES1998B[]
INVOICE_DATE|INVOICE_NUMBER|CLIENT_ID|LAW_FIRM_MATTER_ID|INVOICE_TOTAL|BILLING_START_DATE|BILLING_END_DATE|INVOICE_DESCRIPTION|LINE_ITEM_NUMBER|EXP/FEE/INV_ADJ_TYPE|LINE_ITEM_NUMBER_OF_UNITS|LINE_ITEM_ADJUSTMENT_AMOUNT|LINE_ITEM_TOTAL|LINE_ITEM_DATE|LINE_ITEM_TASK_CODE|LINE_ITEM_EXPENSE_CODE|LINE_ITEM_ACTIVITY_CODE|TIMEKEEPER_ID|LINE_ITEM_DESCRIPTION|LAW_FIRM_ID|LINE_ITEM_UNIT_COST|TIMEKEEPER_NAME|TIMEKEEPER_CLASSIFICATION|CLIENT_MATTER_ID[]
19990225|96542|00711|0528|1684.45|19990101|19990131|For services rendered|1|F|2.00|-70|630|19990115|L510||A102|22547|Research Attorney's fees, Set off claim|24-6437381|350|Arnsley, Robert|PARTNR|423-987[]
"""
        result = self.parser.parse(data)
        self.assertIsNotNone(result)
        self.assertIn("LEDES1998B", result.pretty())

    def test_parse_empty_file(self):
        data = ""
        with self.assertRaises(Exception):
            self.parser.parse(data)

    def test_parse_incorrect_format(self):
        data = """
NOT_THE_SPEC[]
INVOICE_DATE|INVOICE_NUMBER|CLIENT_ID|LAW_FIRM_MATTER_ID|INVOICE_TOTAL|BILLING_START_DATE|BILLING_END_DATE|INVOICE_DESCRIPTION|LINE_ITEM_NUMBER|EXP/FEE/INV_ADJ_TYPE|LINE_ITEM_NUMBER_OF_UNITS|LINE_ITEM_ADJUSTMENT_AMOUNT|LINE_ITEM_TOTAL|LINE_ITEM_DATE|LINE_ITEM_TASK_CODE|LINE_ITEM_EXPENSE_CODE|LINE_ITEM_ACTIVITY_CODE|TIMEKEEPER_ID|LINE_ITEM_DESCRIPTION|LAW_FIRM_ID|LINE_ITEM_UNIT_COST|TIMEKEEPER_NAME|TIMEKEEPER_CLASSIFICATION|CLIENT_MATTER_ID[]
19990225|96542|00711|0528|1684.45|19990101|19990131|For services rendered|1|F|2.00|-70|630|19990115|L510||A102|22547|Research Attorney's fees, Set off claim|24-6437381|350|Arnsley, Robert|PARTNR|423-987[]
"""
        with self.assertRaises(Exception):
            self.parser.parse(data)

    # def test_parse_single_row(self):
    #     data = "LEDES98B\nfield1|field2|field3\n"
    #     result = self.parser.parse(data)
    #     self.assertIsNotNone(result)
    #     self.assertIn("field1", result.pretty())
    #     self.assertIn("field2", result.pretty())
    #     self.assertIn("field3", result.pretty())

    # def test_parse_multiple_rows(self):
    #     data = "LEDES98B\nfield1|field2|field3\nfield4|field5|field6\n"
    #     result = self.parser.parse(data)
    #     self.assertIsNotNone(result)
    #     self.assertIn("field4", result.pretty())
    #     self.assertIn("field5", result.pretty())
    #     self.assertIn("field6", result.pretty())


if __name__ == "__main__":
    unittest.main()
