from time import sleep
from django.test import TestCase

from . import on_install, on_billing_plan_change, on_uninstall, on_login


class CrmEventsTestCase(TestCase):
    def setUp(self):
        self.shop_data = {
            "name": "test_shop",
            "domain": "test_shop.myshopify.com",
            "email": "test@domain.com",
            "phone": "1234567890",
            "country": "CO",
        }
        self.user_data = {
            "first_name": "test",
            "last_name": "user",
            "email": "test@domain.com",
            "phone": "(604) 540 73 38",
        }
        self.users_data = [
            self.user_data,
        ]

    def test_on_install(self):
        on_install(self.shop_data)

    # def test_on_login(self):
    #     on_login(self.shop_data, self.user_data)

    # def test_on_billing_activation(self):
    #     print("test_on_billing_activation")
    #     on_billing_plan_change(self.shop_data, 10)

    # def test_on_uninstall(self):
    #     on_uninstall(self.shop_data, self.users_data)
