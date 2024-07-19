import random
import string
from typing import Optional, Protocol

import pytest
from faker import Faker
from faker.providers import BaseProvider


def fake_alphanumeric_id(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


class InvoiceDataFaker(Protocol):
    def invoice_number(self) -> str:
        ...

    def client_id(self, length: int = 10) -> str:
        ...

    def law_firm_matter_id(self, length: int = 10) -> str:
        ...


class AlphanumericIDProvider(
    BaseProvider,
):
    def invoice_number(self, length: Optional[int] = None) -> str:
        return fake_alphanumeric_id(length or self.random_int(1, 20))

    def client_id(self, length: Optional[int] = None) -> str:
        return fake_alphanumeric_id(length or self.random_int(1, 20))

    def law_firm_matter_id(self, length: Optional[int] = None) -> str:
        return fake_alphanumeric_id(length or self.random_int(1, 20))


@pytest.fixture(scope="session", autouse=True)
def invoice_faker() -> InvoiceDataFaker:
    # Create a Faker instance and add custom providers
    fake = Faker()
    fake.add_provider(AlphanumericIDProvider)
    return fake
