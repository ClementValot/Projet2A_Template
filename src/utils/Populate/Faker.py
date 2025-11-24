from typing import Tuple

from faker import Faker
from faker.providers import BaseProvider, DynamicProvider
from faker.providers.address.fr_FR import Provider as address_provider

from src.Service.PasswordService import create_salt, hash_password

fake = Faker("fr_FR")

item_type_provider = DynamicProvider(
    provider_name="item_type",
    elements=["Main course", "Drink", "Dessert", "Side dish", "Starter"],
)
item_name_provider = DynamicProvider(
    provider_name="item_name", elements=["Deluxe", "Special", "Classic", "Premium", "Gourmet"]
)
bundle_name_provider = DynamicProvider(
    provider_name="bundle_name", elements=["Menu", "Combo", "Package", "Deal", "Special"]
)


class PasswordProvider(BaseProvider):
    def create_salt(self) -> str:
        return create_salt()

    def create_hash_password(self, name: str) -> Tuple[str, str]:
        salt = create_salt()
        return (salt, hash_password(name + str(len(name)), salt))


fake.add_provider(address_provider)
fake.add_provider(item_type_provider)
fake.add_provider(item_name_provider)
fake.add_provider(bundle_name_provider)
fake.add_provider(PasswordProvider)
