from src.CLI.abstract_view import AbstractView
from src.CLI.auth_view import AuthView


class DriverMainView(AbstractView):
    def display(self):
        auth_view = AuthView(self.session, self.services)
        if not self.session.is_authenticated():
            auth_view.display()

        if not self.session.is_authenticated():
            return

        if self.session.role != "driver":
            print("Access denied. This menu is for drivers only.")
            return

        while True:
            print("\n=== EJR Eats — Driver Menu ===")
            print("1) View pending order")
            print("2) Create delivery")
            print("3) Get your deliveries ID")
            print("4) Get itinerary")
            print("5) Get delivery details")
            print("6) Mark delivery as completed")

            print("q) Logout")
            choice = self.prompt("Choice: ")

            if choice == "1":
                self._view_pending_order()
            elif choice == "2":
                self._assign_delivery()
            elif choice == "3":
                self._get_assigned_deli()
            elif choice == "4":
                self._get_itinerary()
            elif choice == "5":
                self._get_delivery_details()
            elif choice == "6":
                self._complete_delivery()
            elif choice.lower() == "q":
                self.session.logout()
                print("Logged out.")
                return
            else:
                self.print_error("Invalid choice.")

    def _view_pending_order(self):
        driver_service = self.services.get("driver")
        try:
            orders = driver_service.list_pending_orders()
            if not orders:
                print("No pending orders.")
                return

            for o in orders:
                address = (
                    f"{o.address.street_number},{o.address.street_name}, {o.address.city}"
                    if o.address
                    else "No address"
                )
                print(f"Order #{o.id_order} - Status: {o.status} - Address: {address}")

        except Exception as e:
            self.print_error(f"Error retrieving orders: {e}")

    def _assign_delivery(self):
        driver_service = self.services.get("driver")
        order_service = self.services.get("order")
        order_ids = []
        while True:
            print("Validate your delivery with V")
            choice = self.prompt("Or add Order by entering its id : \n")
            if choice.upper() == "V":
                if not order_ids:
                    print("Add at least one order in your delivery\n")
                    continue
                else:
                    break
            else:
                try:
                    order_id = int(choice)
                    if order_service.find_order_by_id(order_id) in driver_service.list_pending_orders():
                        if order_id not in order_ids:
                            order_ids.append(order_id)
                            print(f"Order ID {order_id} added.")
                            print(f"Current orders in your delivery : {order_ids}")
                        else:
                            self.print_error(f"Order ID {order_id} is already in the list.")
                    else:
                        self.print_error(f"Order ID {order_id} is not pending.")

                except ValueError:
                    self.print_error("Invalid input. Please enter a valid Order ID (integer) or 'V' to validate.")
        try:
            new_del = driver_service.create_and_assign_delivery(order_ids, self.session.user_id)
            self.print_info(f"Assigned to delivery #{new_del.id_delivery}.")
        except Exception as e:
            self.print_error(f"Assignment failed: {e}")
            new_del = driver_service.create_and_assign_delivery(order_ids, self.session.user_id)

    def _get_itinerary(self):
        driver_service = self.services.get("driver")
        driver_service.get_itinerary(self.session.user_id)

    def _get_assigned_deli(self):
        driver_service = self.services.get("driver")
        res = driver_service.get_assigned_delivery(self.session.user_id)
        if not res:
            print("Your does not have any delivery assigned \n")
            return res
        else:
            list_delivery = [d.id_delivery for d in res]
            print("Here are your assigned deliveries :\n")
            print(list_delivery)
            return list_delivery

    def _get_delivery_details(self):
        driver_service = self.services.get("driver")
        delivery_id = int(self.prompt("Which Delivery ID :"))
        print(driver_service.get_delivery_details(delivery_id))

    def _complete_delivery(self):
        delivery_service = self.services.get("driver")
        delivery_id = int(self.prompt("Delivery ID to mark complete: "))
        try:
            delivery_service.complete_delivery(delivery_id)
            self.print_info(f"Delivery #{delivery_id} marked as completed.")
        except Exception as e:
            self.print_error(f"Completion failed: {e}")
