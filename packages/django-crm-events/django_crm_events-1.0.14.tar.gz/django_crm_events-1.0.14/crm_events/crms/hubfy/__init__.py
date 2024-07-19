import requests

from django.conf import settings

from ..base_service import BaseService


class Hubfy(BaseService):

    def __init__(self) -> None:
        self.api_key = getattr(settings, "HUBFY_API_SECRET", None)
        self.account_name = getattr(settings, "HUBFY_ACCOUNT_NAME", None)
        self.app_name = getattr(settings, "CRM_APP_NAME", None)
        super().__init__()

    def on_login(self, shop_data, user_data):
        print(user_data)
        data = {
            "name": "user_login",
            "data": {
                "app_alias": self.app_name,
                "user": {
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "phone": user_data["phone"],
                    "shopify_rest_id": None,
                },
                "shop": {
                    "shopify_domain": shop_data["domain"],
                    "shopify_rest_id": None,
                    "phone": shop_data["phone"],
                },
            },
        }
        self.post(data)

    def is_available(self):
        if self.api_key and self.app_name and self.account_name:
            return True
        else:
            return False

    def post(self, data):
        response = requests.post(
            f"https://hubfy.moship.io/{self.account_name}/api/v1/events/",
            json=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        print(response.text)
        return response

    def on_install(self, shop_data):
        self.on_login(
            shop_data,
            {
                "first_name": "Shop",
                "last_name": "Contact",
                "email": "",
                "phone": shop_data["phone"],
            },
        )
