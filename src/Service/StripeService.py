import os
from typing import Dict

import stripe
from stripe._error import StripeError
from stripe.checkout import Session

from src.Model.Order import Order
from src.utils.log_decorator import log


class StripeService:
    def __init__(self):
        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        self.base_url = os.environ["BASE_URL"]
        self.success_url = f"{self.base_url}payment/success"
        self.cancel_url = f"{self.base_url}menu"

    @log
    def create_checkout_session(self, order: Order, customer_mail: str) -> Dict:
        """
        Create a checkout session with the order infos
        that will redirect the user to the payment page.

        Parameters
        ----------
        order : Order
            The order that will be paid
        customer_mail : str
            The unique mail of the customer

        Returns
        -------
        Dict
            A dictionnary with the url to the payment page and the id of the checkout session

        Raises
        ------
        ValueError
            If the shopping cart is empty
        ValueError
            If an error occured during the creation of the session
        """
        if len(order.order_orderables) == 0:
            raise ValueError("Your order is empty.")

        line_items = []

        for orderable, quantity in order.order_orderables.items():
            if orderable.orderable_type == "item":
                orderable_name = orderable.item_name
                orderable_description = orderable.item_description

            if orderable.orderable_type == "bundle":
                orderable_name = orderable.bundle_name
                orderable_description = orderable.bundle_description

            price = int(orderable.price * 100)

            data = {
                "price_data": {
                    "currency": "eur",
                    "unit_amount": price,
                    "product_data": {"name": orderable_name, "description": orderable_description},
                },
                "quantity": quantity,
            }
            line_items.append(data)

        try:
            session = Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=f"{self.success_url}?session_id={{CHECKOUT_SESSION_ID}}"
                f"&order_id={order.order_id}",
                cancel_url=self.cancel_url,
                customer_email=customer_mail,
                metadata={
                    "order_id": str(order.order_id),
                    "customer_id": str(order.order_customer_id),
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(order.order_id),
                    }
                },
            )
            return {"url": session.url, "id": session.id}

        except StripeError as e:
            raise ValueError(f"Error while creating Stripe checkout session: {str(e)}") from e

    @log
    def verify_payment(self, session_id: int) -> Dict:
        """
        Retrieve a checkout session to check that it was correctly paid

        Parameters
        ----------
        session_id : int
            The unique id of the checkout session

        Returns
        -------
        Dict
            A dictionnary :
                - paid: bool
                    True if the order was correctly paid else False
                -payment_status: str
                    The payment status

        Raises
        ------
        ValueError
            If an error occured while retrieving the checkout session
        """
        try:
            session = Session.retrieve(session_id)

            return {
                "paid": session.payment_status == "paid",
                "payment_status": session.payment_status,
            }

        except StripeError as e:
            raise ValueError(f"Error while retrieving payment status: {str(e)}") from e
