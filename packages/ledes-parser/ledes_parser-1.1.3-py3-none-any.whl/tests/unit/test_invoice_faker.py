from typing import Union

from faker import Faker

from tests.conftest import InvoiceDataFaker


def test_fake_invoice_number_is_alphanumeric(
    invoice_faker: Union[Faker, InvoiceDataFaker]
):
    fake = invoice_faker
    invoice_number = fake.invoice_number()

    assert invoice_number
    assert invoice_number.isalnum()
