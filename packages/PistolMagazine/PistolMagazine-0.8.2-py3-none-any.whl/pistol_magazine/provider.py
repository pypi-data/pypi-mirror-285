from faker import Faker

fake = Faker()


def provider(cls):
    provider_instance = cls()
    fake.add_provider(provider_instance)
    return cls
