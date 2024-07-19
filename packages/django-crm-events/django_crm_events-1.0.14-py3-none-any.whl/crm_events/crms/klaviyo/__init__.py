from django.conf import settings

from ..base_service import BaseService


class Klaviyo(BaseService):
    def __init__(self) -> None:
        self.KLAVIYO_PUBLIC_API_KEY = getattr(settings, "KLAVIYO_PUBLIC_API_KEY", None)
        self.KLAVIYO_SECRET_API_KEY = getattr(settings, "KLAVIYO_SECRET_API_KEY", None)

    def on_login(self, shop, user):
        print("klaviyo on_login")

    def on_billing_plan_change(self, shop, monthly_price):
        print("klaviyo on_billing_plan_change")

    def on_uninstall(self, shop_data, users_data):
        print("klaviyo on_uninstall")

    def is_available(self):
        if self.KLAVIYO_PUBLIC_API_KEY is None:
            return False
        if self.KLAVIYO_SECRET_API_KEY is None:
            return False
        return True
