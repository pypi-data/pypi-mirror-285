from datetime import date, timedelta
import difflib
import logging
import requests
import json


logger = logging.getLogger(__name__)


class ZenotiGuest:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        birthday: str,
        gender: str,
        center_name: str,
        height: int,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birthday = birthday
        self.gender = gender
        self.center_name = center_name
        self.height = height


class Zenoti:
    def __init__(
        self,
        zenoti_username,
        zenoti_password,
        zenoti_token,
        zenoti_app_id,
    ):
        try:
            payload = json.dumps(
                {
                    "account_name": "options",
                    "user_name": zenoti_username,
                    "password": zenoti_password,
                    "grant_type": "password",
                    "app_id": zenoti_app_id,
                    "app_secret": zenoti_token,  # noqa
                    "device_id": "script",
                }
            )
            headers = {"Content-Type": "application/json"}

            token = requests.request(
                "POST",
                "https://api.zenoti.com/v1/tokens",
                headers=headers,
                data=payload,  # noqa
            ).json()["credentials"]["access_token"]
            self.token = token
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_guest_height(self, guest_id) -> int:
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            response = requests.request(
                "GET",
                f"https://api.zenoti.com/v1/Guests/{guest_id}/Forms",
                headers=headers,
            )
            data = json.loads(response.json()["data"])
            for row in data:
                if row["name"] == "txtHeight":
                    height = row["value"]
                    feet = height.split("ft")[0]
                    inches = height.split("ft ")[1].split(" in")[0]
                    h_inch = int(feet) * 12 + int(inches)
                    cm = round(h_inch * 2.54)
                    return cm
        except Exception as e:
            return 0

    def get_guest_details_by_id(self, guest_id) -> ZenotiGuest:
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            response = requests.request(
                "GET",
                f"https://api.zenoti.com/v1/guests/{guest_id}",
                headers=headers,
            )

            height = self.get_guest_height(guest_id)

            guest_object = response.json()
            personal_info = guest_object["personal_info"]
            return ZenotiGuest(
                personal_info["first_name"],
                personal_info["last_name"],
                personal_info["email"],
                (
                    personal_info["mobile_phone"]["number"]
                    if personal_info["mobile_phone"]
                    else "1234567890"
                ),
                (
                    personal_info["date_of_birth"].split("T")[0]
                    if personal_info["date_of_birth"]
                    else "1970-01-01"
                ),
                "male" if personal_info["gender"] > 0 else "female",
                guest_object["center_name"],
                height,
            )
        except requests.exceptions.RequestException as e:
            self.flask_app.logger.info(e)
            return ZenotiGuest("", "", "", "", "", "", "")

    def apply_promo(self, invoice_id: str, center_id: str, shopify_promo: str):  # noqa
        try:
            apply_promo_code = requests.post(
                f"https://api.zenoti.com/v1/invoices/{invoice_id}/campaign_discount/apply",  # noqa
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
                json={"offer_code": shopify_promo, "center_id": center_id},
            )
            return apply_promo_code.status_code
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def mark_invoice_refunded_zenoti(self, invoice_id: int) -> int:
        try:
            refunded_update = requests.post(
                f"https://api.zenoti.com/v1/invoices/{invoice_id}/close",
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
                json={"status": -1},
            )

            return refunded_update.status_code
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def add_address_to_zenoti_guest(
        self,
        guestInfo: dict,
        address1: str,
        address2: str,
        city: str,
        state: str,
        zipcode: str,
    ):
        try:
            getStates = requests.get(
                "https://api.zenoti.com/v1/countries/225/states",
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
            ).json()
            stateID = ""
            for state_obj in getStates["states"]:
                if state_obj["name"] == state:
                    stateID = state_obj["id"]
            address_info = {
                "address_1": address1,
                "address_2": address2,
                "city": city,
                "country_id": 225,
                "state_id": stateID,
                "state_other": "",
                "zip_code": zipcode,
            }
            guestInfo["address_info"] = address_info
            add_address = requests.put(
                f"https://api.zenoti.com/v1/guests/{guestInfo['id']}?expand=address_info",  # noqa
                json=guestInfo,
                headers={
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
            ).json()
            return add_address
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def mark_invoice_closed(self, invoice_id: id, payment_id: str) -> int:
        try:
            # custom payment
            invoice = requests.get(
                f"https://api.zenoti.com/v1/invoices/{invoice_id}?expand=InvoiceItems&expand=Transactions",  # noqa
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
            ).json()["invoice"]

            if invoice["total_price"] is not None:
                requests.post(
                    f"https://api.zenoti.com/v1/invoices/{invoice_id}/payment/custom",  # noqa
                    headers={
                        "application_version": "1.0.0",
                        "Authorization": f"bearer {self.token}",
                        "Content-Type": "application/json",
                        "application_name": "Shopify Connection",
                    },
                    json={
                        "amount": invoice["total_price"]["sum_total"],
                        "custom_payment_id": payment_id,
                    },
                )

            # close invoice
            close_invoice = requests.request(
                "POST",
                f"https://api.zenoti.com/v1/invoices/{invoice_id}/close",
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
            )
            return close_invoice.status_code
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_existing_guest_info_by_phone(self, order):
        try:
            return requests.get(
                f"https://api.zenoti.com/v1/guests/search?phone={order.phone}&expand=primary_employee",  # noqa
                headers={
                    "accept": "application/json",
                    "Authorization": f"bearer {self.token}",
                },
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_existing_guest_info_by_email(self, order):
        try:
            return requests.get(
                f"https://api.zenoti.com/v1/guests/search?email={order.email}&expand=primary_employee",  # noqa
                headers={
                    "accept": "application/json",
                    "Authorization": f"bearer {self.token}",
                },
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_zenoti_product_id_from_sku(self, center: str, sku: str) -> str:  # noqa
        try:
            zenoti_products = []
            page = 0
            while len(zenoti_products) % 100 == 0:  # to ensure we paginate
                products = requests.get(
                    f"https://api.zenoti.com/v1/centers/{center}/products?size=100&page={page}",  # noqa
                    headers={
                        "application_version": "1.0.0",
                        "Authorization": f"bearer {self.token}",
                        "Content-Type": "application/json",
                        "application_name": "Shopify Connection",
                    },
                ).json()
                if "products" in products:
                    zenoti_products.extend(products["products"])
                    page = page + 1
            for item in zenoti_products:
                if item["code"] == sku:
                    return item["id"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_center_id_from_center_name(self, shopify_location: str) -> str:  # noqa
        try:
            zenoti_centers = requests.get(
                "https://api.zenoti.com/v1/centers/",
                headers={
                    "accept": "application/json",
                    "Authorization": f"bearer {self.token}",
                },
            ).json()["centers"]
            zenoti_center_names = [
                zenoti_center["name"] for zenoti_center in zenoti_centers
            ]
            closest_zenoti_center = difflib.get_close_matches(
                shopify_location, zenoti_center_names, n=1, cutoff=0
            )[0]
            zenoti_center_id = [
                zenoti_center["id"]
                for zenoti_center in zenoti_centers
                if zenoti_center["name"] == closest_zenoti_center
            ]
            return zenoti_center_id[0]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def create_membership(self, center_id, user_id, membership_id, default_employee_id):
        try:
            membership_invoice = requests.post(
                "https://api.zenoti.com/v1/invoices/memberships",
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
                json={
                    "center_id": center_id,
                    "user_id": user_id,
                    "membership_ids": membership_id,
                    "sale_by_id": default_employee_id,
                },
            ).json()
            return membership_invoice["invoice_id"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def create_consumable(self, center_id, user_id, employee_id, consumable_id):
        try:
            consumable_invoice = requests.post(
                "https://api.zenoti.com/v1/invoices/packages",
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
                json={
                    "guest_id": user_id,
                    "center_id": center_id,
                    "notes": "",
                    "package_details": [
                        {
                            "id": consumable_id,
                            "sale_by_id": employee_id,
                        }
                    ],
                },
            ).json()
            return consumable_invoice["invoice_id"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def create_guest(self, order):
        try:
            guest = requests.post(
                "https://api.zenoti.com/v1/guests",
                json={
                    "center_id": order.center_id,
                    "personal_info": {
                        "first_name": order.first_name,
                        "last_name": order.last_name,
                        "email": order.email,
                        "phone": order.phone,
                    },
                },
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
            ).json()
            return guest
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def create_invoice(self, order, guest_info):
        try:
            invoice = requests.request(
                "POST",
                "https://api.zenoti.com/v1/invoices/products",
                data=json.dumps(
                    {
                        "center_id": order.center_id,
                        "guest_id": guest_info["id"],
                        "notes": order.note,
                        "products": order.items,
                    }
                ),
                headers={
                    "application_version": "1.0.0",
                    "Authorization": f"bearer {self.token}",
                    "Content-Type": "application/json",
                    "application_name": "Shopify Connection",
                },
            ).json()
            return invoice
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_center_id_from_center_name(self, shopify_location: str) -> str:  # noqa
        try:
            zenoti_centers = requests.get(
                "https://api.zenoti.com/v1/centers/",
                headers={
                    "accept": "application/json",
                    "Authorization": f"bearer {self.token}",
                },
            ).json()["centers"]
            zenoti_center_names = [
                zenoti_center["name"] for zenoti_center in zenoti_centers
            ]
            closest_zenoti_center = difflib.get_close_matches(
                shopify_location, zenoti_center_names, n=1, cutoff=0
            )[0]
            zenoti_center_id = [
                zenoti_center["id"]
                for zenoti_center in zenoti_centers
                if zenoti_center["name"] == closest_zenoti_center
            ]
            return zenoti_center_id[0]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

    def get_stock_quantity_of_product(self, center_id, sku):
        # today = date.today() + timedelta(days=1)
        try:
            response = requests.get(
                f"https://api.zenoti.com/v1/inventory/stock?center_id={center_id}&inventory_date={date.today()+ timedelta(days=1)}&search_string={sku}",
                headers={
                    "accept": "application/json",
                    "Authorization": f"bearer {self.token}",
                },
            )
            products = response.json()["list"]
            for product in products:
                if product["product_code"] == sku:
                    return product
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
