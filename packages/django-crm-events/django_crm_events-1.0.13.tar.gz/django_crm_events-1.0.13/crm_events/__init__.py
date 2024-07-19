import logging
from time import sleep


from .crms.clickup import Clickup
from .crms.klaviyo import Klaviyo
from .crms.pipedrive import PipeDrive
from .crms.hubfy import Hubfy

logger = logging.getLogger(__name__)

services = [PipeDrive, Clickup, Klaviyo, Hubfy]


def get_available_services():
    return [service for service in services if service().is_available()]


def on_install(shop_data):
    for service in get_available_services():
        try:
            service().on_install(shop_data)
        except Exception as e:
            logger.error(str(e))


def on_login(shop_data, user_data, sleep_time=5):
    sleep(sleep_time)
    for service in get_available_services():
        try:
            service().on_login(shop_data, user_data)
        except Exception as e:
            logger.error(str(e))


def on_billing_plan_change(shop_data, monthly_price):
    for service in get_available_services():
        try:
            service().on_billing_plan_change(shop_data, monthly_price)
        except Exception as e:
            logger.error(str(e))


def on_uninstall(shop_data, users_data):
    for service in get_available_services():
        try:
            service().on_uninstall(shop_data, users_data)
        except Exception as e:
            logger.error(str(e))
