from abc import ABC, abstractmethod


class BaseService(ABC):
    def on_install(self, shop):
        print(self.__class__.__name__, "on_install not implemented")

    def on_login(self, shop, user):
        print(self.__class__.__name__, "on_login not implemented")

    def on_billing_plan_change(self, shop, monthly_price):
        print(self.__class__.__name__, "set_shop_plan not implemented")

    def on_uninstall(self, shop, users):
        print(self.__class__.__name__, "on_uninstall not implemented")

    @abstractmethod
    def is_available(self):
        return False
