import random
from datetime import timedelta
from decimal import Decimal
from typing import Union

import pytest
from faker import Faker
from lark import Lark

from ledes_parser.ledes_parser import get_parser
from tests.conftest import InvoiceDataFaker


@pytest.fixture(autouse=True, scope="session")
def parser() -> Lark:
    return get_parser("98B")


def generate_invoice_description(invoice_number: str) -> str:
    """
    From the spec: A descriptive summary of work performed which is charged on this invoice during the applicable billing period. Limited to 15KB of text.
    """
    fake = Faker()
    fake.seed_instance(invoice_number)
    possible_descriptions = [
        "",  # No description
        fake.paragraph(1),  # Short description
        fake.paragraph(5),  # Medium description
        fake.paragraph(10),  # Long description
        fake.paragraph(100),  # Very Long description
    ]
    MAX_KILOBYTES = 15 * 1024
    assert all([len(d.encode("utf-8")) <= MAX_KILOBYTES for d in possible_descriptions])

    return possible_descriptions[random.randint(0, len(possible_descriptions) - 1)]


def test_parse_ledes(parser: Lark, invoice_faker: Union[Faker, InvoiceDataFaker]):
    fake = invoice_faker  # Just to shorten it, while still not conflicting with the `faker` fixture.

    assert parser is not None
    assert fake is not None

    invoice_number = fake.invoice_number()

    fake.seed_instance(invoice_number)
    invoice_date = fake.date_this_century()
    billing_end_date = fake.date_this_month(before_today=True)
    billing_start_date = billing_end_date - timedelta(days=random.randint(30, 180))

    line_item = {
        "INVOICE_DATE": invoice_date,
        "INVOICE_NUMBER": invoice_number,
        "CLIENT_ID": fake.client_id(),
        "LAW_FIRM_MATTER_ID": fake.law_firm_matter_id(),
        "INVOICE_TOTAL": Decimal(1000.00),
        "BILLING_START_DATE": billing_start_date,
        "BILLING_END_DATE": billing_end_date,
        "INVOICE_DESCRIPTION": generate_invoice_description(invoice_number),
        "LINE_ITEM_NUMBER": None,
        "EXP_FEE_INV_ADJ_TYPE": None,
        "LINE_ITEM_NUMBER_OF_UNITS": None,
        "LINE_ITEM_ADJUSTMENT_AMOUNT": None,
        "LINE_ITEM_TOTAL": None,
        "LINE_ITEM_DATE": None,
        "LINE_ITEM_TASK_CODE": None,
        "LINE_ITEM_EXPENSE_CODE": None,
        "LINE_ITEM_ACTIVITY_CODE": None,
        "TIMEKEEPER_ID": None,
        "LINE_ITEM_DESCRIPTION": None,
        "LAW_FIRM_ID": None,
        "LINE_ITEM_UNIT_COST": None,
        "TIMEKEEPER_NAME": None,
        "TIMEKEEPER_CLASSIFICATION": None,
        "CLIENT_MATTER_ID": None,
    }

    assert line_item is not None


if __name__ == "__main__":
    test_parse_ledes()
