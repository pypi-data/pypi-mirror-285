from functools import cached_property
from cachetools import cached
import requests
from django.conf import settings

from crm_events.utils import print_dict

from ..base_service import BaseService
from .exceptions import DealNotFound, OrganizationNotFound, PersonNotFound


class PipeDrive(BaseService):
    def __init__(self) -> None:
        self.api_key = getattr(settings, "PIPEDRIVE_PERSONAL_API_KEY", None)
        self.app_name = getattr(settings, "CRM_APP_NAME", None)
        self.intalled_pipeline_id = getattr(
            settings, "PIPEDRIVE_INSTALLED_PIPELINE_ID", None
        )
        self.uninstalled_pipeline_id = getattr(
            settings, "PIPEDRIVE_UNINSTALLED_PIPELINE_ID", None
        )

    def on_install(self, shop_data):
        organization = self.get_or_create_organization(shop_data)
        self.update_organization_fields(organization, shop_data)
        person = self.get_or_create_person(
            organization,
            {
                "first_name": shop_data["name"],
                "last_name": "",
                "email": shop_data["email"],
                "phone": shop_data["phone"],
            },
        )
        deal = self.get_or_create_deal(
            organization, shop_data, "install", person_id=person["id"]
        )
        self.add_note_to_deal(deal, shop_data)

    def on_billing_plan_change(self, shop_data, monthly_price):
        organization = self.get_or_create_organization(shop_data)
        self.update_organization_fields(
            organization, shop_data, plan_price=monthly_price
        )

    def on_login(self, shop_data, user_data):
        organization = self.get_or_create_organization(shop_data)
        self.update_organization_fields(organization, shop_data)
        self.get_or_create_person(organization, user_data)
        # add person to organization if already exists

    def on_uninstall(self, shop_data, users_data):
        organization = self.get_or_create_organization(shop_data)
        self.get_or_create_deal(organization, shop_data, "uninstall")

    def is_available(self):
        if not self.api_key:
            return False
        if not self.app_name:
            return False
        if not self.intalled_pipeline_id:
            return False
        if not self.uninstalled_pipeline_id:
            return False
        return True

    def get(self, path):
        return requests.get(
            f"https://api.pipedrive.com/v1/{path}", params={"api_token": self.api_key}
        )

    def post(self, path, data):
        return requests.post(
            f"https://api.pipedrive.com/v1/{path}",
            params={"api_token": self.api_key},
            data=data,
        )

    def put(self, path, data):
        return requests.put(
            f"https://api.pipedrive.com/v1/{path}",
            params={"api_token": self.api_key},
            json=data,
        )

    def get_or_create_organization(self, shop_data):
        try:
            return self.get_organization(shop_data)
        except OrganizationNotFound:
            return self.create_organization(shop_data)

    def get_organization_details(self, organization_id):
        response = self.get(f"organizations/{organization_id}")
        response.raise_for_status()
        return response.json()["data"]

    def get_organization(self, shop_data):
        response = self.get(f"organizations/find?term={shop_data['domain']}")

        response.raise_for_status()
        data = response.json()["data"]
        if len(data) == 0:
            raise OrganizationNotFound()
        for organization in data:
            if organization["name"] == shop_data["domain"]:
                return self.get_organization_details(organization["id"])

        raise OrganizationNotFound()

    def create_organization(self, shop_data):
        response = self.post(
            "organizations",
            {
                "name": shop_data["domain"],
            },
        )
        response.raise_for_status()
        return response.json()["data"]

    @cached_property
    def organization_custom_fields(self):
        response = self.get("/organizationFields")
        response.raise_for_status()
        return response.json()["data"]

    def get_organization_field(self, field_name):
        for field in self.organization_custom_fields:
            if field["name"].lower() == field_name.lower():
                return field
        return None

    def organization_data_add_or_remove_app(
        self, organization, data, field_data, action="add"
    ):
        if not field_data:
            return data

        def get_app_id(field_data):
            for option in field_data["options"]:
                if option["label"].lower() == self.app_name.lower():
                    return option["id"]
            return None

        current_apps = organization[field_data["key"]]

        if not current_apps:
            current_apps = []
        else:
            current_apps = current_apps.split(",")

        app_id = str(get_app_id(field_data))

        if action == "add":
            if app_id not in current_apps:
                current_apps.append(app_id)
                data[field_data["key"]] = current_apps

        if action == "remove":
            if app_id in current_apps:
                current_apps.remove(app_id)
                data[field_data["key"]] = current_apps

        return data

    def update_organization_fields(
        self, organization, shop_data, action="install", plan_price=None
    ):
        data = {}

        country_code_field = self.get_organization_field("Country Code")
        if country_code_field:
            data[country_code_field["key"]] = shop_data["country"]

        shop_name_code_field = self.get_organization_field("Shop Name")
        if shop_name_code_field:
            data[shop_name_code_field["key"]] = shop_data["name"]

        if action == "install":
            installed_apps_field = self.get_organization_field("Installed Apps")
            data = self.organization_data_add_or_remove_app(
                organization, data, installed_apps_field
            )

        if plan_price != None:
            active_billing_plan_field = self.get_organization_field("Active Billing")
            data = self.organization_data_add_or_remove_app(
                organization,
                data,
                active_billing_plan_field,
                action="add" if plan_price != 0 else "remove",
            )

        response = self.put(f"organizations/{organization['id']}", data)
        response.raise_for_status()

    def get_or_create_deal(self, organization, shop_data, action, person_id=None):
        try:
            return self.get_deal(shop_data, action)
        except DealNotFound:
            return self.create_deal(
                organization, shop_data, action, person_id=person_id
            )

    def create_deal_name(self, shop_data, action):
        prefix = "I" if action == "install" else "U"
        return f"{prefix} - {self.app_name} - {shop_data['domain']}"

    def get_deal_status(self, monthly_price):
        return "won" if monthly_price != 0 else "lost"

    def get_deal(self, shop_data, action):
        deal_name = self.create_deal_name(shop_data, action)
        response = self.get(f"deals/search?term={deal_name}")
        response.raise_for_status()
        data = response.json()["data"]

        if len(data) == 0:
            raise DealNotFound()

        for deal in data["items"]:
            if deal["item"]["title"] == deal_name:
                return deal["item"]

        raise DealNotFound()

    def create_deal(self, organization, shop_data, action, person_id=None):
        deal_name = self.create_deal_name(shop_data, action)
        if action == "install":
            pipeline_id = self.intalled_pipeline_id
        else:
            pipeline_id = self.uninstalled_pipeline_id

        deal_data = {
            "title": deal_name,
            "org_id": organization["id"],
            "currency": "USD",
            "status": "open",
            "pipeline_id": pipeline_id,
        }

        if person_id:
            deal_data["person_id"] = person_id

        response = self.post("deals", deal_data)
        response.raise_for_status()
        return response.json()["data"]

    def set_deal_status(self, deal, monthly_price):
        status = self.get_deal_status(monthly_price)
        response = self.put(
            f"deals/{deal['id']}",
            {
                "status": status,
                "currency": "USD",
                "value": monthly_price,
            },
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_or_create_person(self, organization, user_data):
        try:
            return self.get_person(organization, user_data)
        except PersonNotFound:
            return self.create_person(organization, user_data)

    def get_person(self, organization, user_data):
        response = self.get(
            f"persons/search?term={user_data['email']}&organization_id={organization['id']}"
        )
        response.raise_for_status()
        data = response.json()["data"]["items"]

        if len(data) == 0:
            raise PersonNotFound()

        for person in data:
            person = person["item"]
            for email in person["emails"]:
                if email == user_data["email"]:
                    return person

        raise PersonNotFound()

    def create_person(self, organization, user_data):
        response = self.post(
            "persons",
            {
                "name": f"{user_data['first_name']} {user_data['last_name']}",
                "org_id": organization["id"],
                "email": user_data["email"],
                "phone": user_data["phone"],
                "marketing_status": "subscribed",
            },
        )
        response.raise_for_status()
        return response.json()["data"]

    def add_note_to_deal(self, deal, shop_data):
        note = f"""
            Shopify store {shop_data['name']} has been installed <br>
            website: {shop_data['domain']}<br/>
            phone: {shop_data['phone']}<br/>
            email: {shop_data['email']}<br/>
            country: {shop_data['country']}<br/>
        """
        response = self.post(
            "notes",
            {
                "content": note,
                "deal_id": deal["id"],
            },
        )
        response.raise_for_status()
        return response.json()["data"]
