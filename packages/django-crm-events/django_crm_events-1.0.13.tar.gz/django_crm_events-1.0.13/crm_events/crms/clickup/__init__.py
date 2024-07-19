import json
from django.conf import settings
import requests
from ..base_service import BaseService
from .exceptions import (
    ContactNotFound,
    ShopNotFound,
    AppShopNotFound,
    DropdownOptionException,
)


class Clickup(BaseService):
    def __init__(
        self,
        clickup_api_key=None,
        shop_list_id=None,
        app_shops_list_id=None,
        contacts_list_id=None,
        app_name=None,
    ) -> None:
        self.clickup_api_key = clickup_api_key or getattr(
            settings, "CLICKUP_PERSONAL_API_KEY", None
        )
        self.shops_list_id = shop_list_id or getattr(
            settings, "CLICKUP_SHOPS_LIST_ID", None
        )
        self.app_shops_list_id = app_shops_list_id or getattr(
            settings, "CLICKUP_APP_SHOPS_LIST_ID", None
        )
        self.contacts_list_id = contacts_list_id or getattr(
            settings, "CLICKUP_CONTACTS_LIST_ID", None
        )
        self.app_name = app_name or getattr(settings, "CRM_APP_NAME", None)
        self.custom_fields = {"list_id": {"field_name": "field_id"}}

    def on_install(self, shop_data):
        shop = self.get_or_create_shop(shop_data)
        shop_app = self.get_or_create_app_shop(shop, creation_status="Installed")
        self.set_task_status(shop_app, "Installed")

    def on_login(self, shop_data, user_data):
        shop = self.get_or_create_shop(shop_data)
        self.get_or_create_app_shop(shop)
        contact = self.get_or_create_contact(shop, user_data)
        self.add_contact_to_shop(contact, shop)

    def on_billing_plan_change(self, shop_data, monthly_price):
        shop = self.get_or_create_shop(shop_data)
        shop_app_status = "Unknown" if monthly_price == 0 else "Active Billing"
        shop_app = self.get_or_create_app_shop(shop, creation_status=shop_app_status)
        shop_app = self.set_task_status(shop_app, shop_app_status)
        self.set_shop_app_plan(shop_app, monthly_price)

    def on_uninstall(self, shop_data, users_data):
        shop = self.get_or_create_shop(shop_data)
        shop_app = self.get_or_create_app_shop(shop, creation_status="Uninstalled")
        shop_app = self.set_task_status(shop_app, "Uninstalled")
        self.set_shop_app_plan(shop_app, 0)

    @property
    def headers(self):
        return {"Authorization": self.clickup_api_key}

    def post(self, url, data):
        return requests.post(url, json=data, headers=self.headers)

    def get(self, url, query=None):
        return requests.get(url, headers=self.headers, params=query)

    def put(self, url, data):
        return requests.put(url, json=data, headers=self.headers)

    def is_available(self):
        if self.clickup_api_key is None:
            return False
        if self.shops_list_id is None:
            return False
        if self.contacts_list_id is None:
            return False
        if self.app_shops_list_id is None:
            return False
        if self.app_name is None:
            return False
        return True

    def update_custom_fields(self, list_id):
        url = f"https://api.clickup.com/api/v2/list/{list_id}/field"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"clickup get_custom_field error: {response.text}")

        fields = response.json()["fields"]
        for field in fields:
            try:
                self.custom_fields[list_id][field["name"].lower()] = field["id"]
            except KeyError:
                list_fields = {field["name"].lower(): field["id"]}
                self.custom_fields[list_id] = list_fields

    def get_custom_field(self, list_id, custom_field_name, is_retry=False):
        custom_field_name = custom_field_name.lower()
        try:
            return self.custom_fields[list_id][custom_field_name]
        except KeyError:
            assert not is_retry, "clickup get_custom_field error"
            self.update_custom_fields(list_id)

            return self.get_custom_field(
                list_id,
                custom_field_name,
                is_retry=True,
            )

    def get_dropdown_field_value(self, custom_fields, field_id):
        for field in custom_fields:
            if field["id"] == field_id:
                if field.get("value") is None:
                    return ""

                index = field["value"]
                return field["type_config"]["options"][index]["name"]

    def get_dropdown_field_option_id(self, customer_fields, field_id, option_name):
        for field in customer_fields:
            if field["id"] == field_id:
                for option in field["type_config"]["options"]:
                    if option["name"].lower() == option_name.lower():
                        return option["id"]
        raise DropdownOptionException("Option not found")

    def create_shop(self, shop_data):
        url = f"https://api.clickup.com/api/v2/list/{self.shops_list_id}/task"

        description = f"""
        Name: {shop_data["name"]}
        Domain: {shop_data["domain"]}
        Email: {shop_data["email"]}
        Phone: {shop_data["phone"]}
        Country: {shop_data["country"]}
        """
        url_field_id = self.get_custom_field(self.shops_list_id, "URL")
        country_field_id = self.get_custom_field(self.shops_list_id, "Country")
        shop_url = f"https://{shop_data['domain']}"
        payload = {
            "name": shop_data["name"],
            "status": "CUSTOMER",
            "description": description,
            "custom_fields": [
                {
                    "id": url_field_id,
                    "value": shop_url,
                },
                {
                    "id": country_field_id,
                    "value": shop_data["country"],
                },
            ],
        }
        response = self.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(f"clickup create_shop error: {response.text}")

        return response.json()

    def get_shop(self, shop_data):
        url_field_id = self.get_custom_field(self.shops_list_id, "URL")
        custom_fields = [
            {
                "field_id": url_field_id,
                "operator": "=",
                "value": shop_data["domain"],
            }
        ]
        query = {
            "archived": True,
            "include_closed": True,
            "custom_fields": json.dumps(custom_fields),
        }
        response = self.get(
            f"https://api.clickup.com/api/v2/list/{self.shops_list_id}/task",
            query=query,
        )
        if response.status_code != 200:
            raise Exception(f"clickup get_shop error: {response.text}")
        tasks = response.json()["tasks"]

        if len(tasks) == 0:
            raise ShopNotFound()
        shop_url = f"https://{shop_data['domain']}"
        for task in tasks:
            for field in task["custom_fields"]:
                if field["id"] == url_field_id and field["value"] == shop_url:
                    return task

        raise ShopNotFound()

    def get_or_create_shop(self, shop_data):
        try:
            shop = self.get_shop(shop_data)
        except ShopNotFound:
            shop = self.create_shop(shop_data)
        return shop

    def get_app_shop(self, clickup_shop):
        shop_task_url_field_id = self.get_custom_field(
            self.app_shops_list_id, "Shop Clickup URL"
        )

        custom_fields = [
            {
                "field_id": shop_task_url_field_id,
                "operator": "=",
                "value": clickup_shop["url"],
            }
        ]
        query = {
            "archived": True,
            "include_closed": True,
            "custom_fields": json.dumps(custom_fields),
        }
        response = self.get(
            f"https://api.clickup.com/api/v2/list/{self.app_shops_list_id}/task",
            query=query,
        )
        if response.status_code != 200:
            raise Exception(f"clickup get_shop error: {response.text}")

        tasks = response.json()["tasks"]

        if len(tasks) == 0:
            raise AppShopNotFound()

        app_field_id = self.get_custom_field(self.app_shops_list_id, "App")

        for task in tasks:
            is_shop = False
            is_app = False

            task_app_field_value = self.get_dropdown_field_value(
                task["custom_fields"], app_field_id
            )

            for field in task["custom_fields"]:
                if (
                    field["id"] == shop_task_url_field_id
                    and field["value"] == clickup_shop["url"]
                ):
                    is_shop = True

                if task_app_field_value.lower() == self.app_name.lower():
                    is_app = True

                if is_shop and is_app:
                    return task

        raise AppShopNotFound()

    def create_app_shop(self, clickup_shop, creation_status=None):
        url = f"https://api.clickup.com/api/v2/list/{self.app_shops_list_id}/task"

        shop_task_url_field_id = self.get_custom_field(
            self.app_shops_list_id, "Shop Clickup URL"
        )

        payload = {
            "name": self.app_name + " | " + clickup_shop["name"],
            "status": creation_status,
            "custom_fields": [
                {
                    "id": shop_task_url_field_id,
                    "value": clickup_shop["url"],
                },
            ],
        }
        response = self.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(f"clickup create_shop error: {response.text}")

        task = response.json()

        shop_field_id = self.get_custom_field(self.app_shops_list_id, "Shop")
        url = f"https://api.clickup.com/api/v2/task/{task['id']}/field/{shop_field_id}"
        payload = {"value": {"add": [clickup_shop["id"]], "rem": []}}
        response = self.post(url, data=payload)

        app_field_id = self.get_custom_field(self.app_shops_list_id, "App")
        url = f"https://api.clickup.com/api/v2/task/{task['id']}/field/{app_field_id}"

        option_id = self.get_dropdown_field_option_id(
            task["custom_fields"], app_field_id, self.app_name
        )

        if option_id:
            payload = {"value": option_id}
            response = self.post(url, data=payload)

        return task

    def get_or_create_app_shop(self, clickup_shop, creation_status=None):
        try:
            app_shop = self.get_app_shop(clickup_shop)
        except AppShopNotFound:
            app_shop = self.create_app_shop(clickup_shop, creation_status)
        return app_shop

    def set_task_status(self, task, status):
        try:
            if task["status"]["status"] == status:
                return task
        except KeyError:
            pass

        url = f"https://api.clickup.com/api/v2/task/{task['id']}"
        payload = {"status": status}
        response = self.put(url, data=payload)
        if response.status_code != 200:
            raise Exception(f"clickup set_task_status error: {response.text}")

        return response.json()

    def set_shop_app_plan(self, shop_app, montly_payment):
        shop_app_plan_field_id = self.get_custom_field(self.app_shops_list_id, "Plan")
        url = f"https://api.clickup.com/api/v2/task/{shop_app['id']}/field/{shop_app_plan_field_id}"
        payload = {"value": montly_payment}
        response = self.post(url, data=payload)

        if response.status_code != 200:
            raise Exception(f"clickup set_shop_app_plan error: {response.text}")

        return response.json()

    def get_or_create_contact(self, clickup_shop, contact_data):
        try:
            contact = self.get_contact(contact_data)
        except ContactNotFound:
            contact = self.create_contact(contact_data)

        return contact

    def get_contact(self, contact_data):
        contact_email_field_id = self.get_custom_field(self.contacts_list_id, "Email")

        custom_fields = [
            {
                "field_id": contact_email_field_id,
                "operator": "=",
                "value": contact_data["email"],
            }
        ]

        query = {
            "archived": True,
            "include_closed": True,
            "custom_fields": json.dumps(custom_fields),
        }
        response = self.get(
            f"https://api.clickup.com/api/v2/list/{self.contacts_list_id}/task",
            query=query,
        )
        if response.status_code != 200:
            raise Exception(f"clickup get_contact error: {response.text}")

        tasks = response.json()["tasks"]

        if len(tasks) == 0:
            raise ContactNotFound()

        for task in tasks:
            for field in task["custom_fields"]:
                if (
                    field["id"] == contact_email_field_id
                    and field["value"] == contact_data["email"]
                ):
                    return task

        raise ContactNotFound()

    def create_contact(self, contact_data):
        url = f"https://api.clickup.com/api/v2/list/{self.contacts_list_id}/task"

        contact_email_field_id = self.get_custom_field(self.contacts_list_id, "Email")
        contact_phone_field_id = self.get_custom_field(self.contacts_list_id, "Phone")

        payload = {
            "name": contact_data["first_name"] + " " + contact_data["last_name"],
            "status": "SHOP USER",
            "custom_fields": [
                {
                    "id": contact_email_field_id,
                    "value": contact_data["email"],
                },
                {
                    "id": contact_phone_field_id,
                    "value": contact_data["phone"],
                },
            ],
        }
        response = self.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(f"clickup create_contact error: {response.text}")

        return response.json()

    def add_contact_to_shop(self, clickup_contact, clickup_shop):
        contacts_field_id = self.get_custom_field(self.shops_list_id, "Contacts")

        url = f"https://api.clickup.com/api/v2/task/{clickup_shop['id']}/field/{contacts_field_id}"

        payload = {"value": {"add": [clickup_contact["id"]], "rem": []}}

        response = self.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(f"clickup add_contact_to_shop error: {response.text}")
