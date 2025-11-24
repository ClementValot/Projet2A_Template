from datetime import datetime
from typing import Dict, List, Optional

from src.DAO.BundleDAO import BundleDAO
from src.Model.Bundle import Bundle
from src.Model.Item import Item
from src.utils.log_decorator import log


class BundleService:
    bundle_dao: BundleDAO

    def __init__(self, bundle_dao: BundleDAO):
        self.bundle_dao = bundle_dao

    @log
    def get_bundle_by_id(self, bundle_id: int) -> Bundle:
        """
        Retrieve a bundle via its unique id

        Parameters
        ----------
        bundle_id : int
            Unique id of the bundle

        Returns
        -------
        Bundle
            A Bundle object with the informations of the retrieved bundle

        Raises
        ------
        ValueError
            If the bundle id is invalid
        """
        bundle = self.bundle_dao.get_bundle_by_id(bundle_id)
        if bundle is None:
            raise ValueError(f"[BundleService] Cannot get: bundle with ID {bundle_id} not found.")
        return bundle

    @log
    def get_bundle_by_orderable_id(self, orderable_id: int) -> Bundle:
        """
        Retrieve a bundle via its orderable id

        Parameters
        ----------
        orderable_id : int
            A unique orderable id

        Returns
        -------
        Bundle
            A Bundle object with the informations of the retrieved bundle

        Raises
        ------
        ValueError
            If the orderable id is invalid
        """
        bundle = self.bundle_dao.get_bundle_by_orderable_id(orderable_id)
        if bundle is None:
            raise ValueError(
                f"[BundleService] Cannot get: bundle with ID {orderable_id} not found."
            )
        return bundle

    @log
    def get_all_bundles(self) -> List[Bundle]:
        """
        Fetch all existing bundles

        Returns
        -------
        List[Bundle]
            A list of Bundle object, an empty list if there is no bundles
        """
        bundles = self.bundle_dao.get_all_bundle()
        return bundles

    @log
    def create_bundle(
        self,
        bundle_name: str,
        bundle_reduction: int,
        bundle_description: str,
        bundle_availability_start_date: datetime,
        bundle_availability_end_date: datetime,
        bundle_items: Dict[Item, int],
        bundle_image: Optional[str] = None,
        is_in_menu: bool = False,
    ) -> Bundle:
        """
        Check all the informations of the bundle, if there is no problem create it

        Checking:
            - The reduction percentage must be between 0 and 100
            - The ending availability date must be after the starting availability date
            - The starting availability date must be later than today

        Parameters
        ----------
        bundle_name : str
            Name of the bundle
        bundle_reduction : int
            Percentage of reduction of the bundle
        bundle_description : str
            Description of the bundle
        bundle_availability_start_date : datetime
            Date at which the bundle will become available
        bundle_availability_end_date : datetime
            Date at which the bundle will become unavailable
        bundle_items : Dict[Item, int]
            A dictionnary with the items and their number in the bundle
        bundle_image : Optional[bytes], optional
            The url to the bundle's image, by default None
        is_in_menu : bool, optional
            If you want to include it in the menu, by default False

        Returns
        -------
        Bundle
            The created bundle

        Raises
        ------
        ValueError
            If the reduction percentage isn't between 0 and 100
        ValueError
            If the ending availability date comes before the starting availability date
        ValueError
            If the starting availibility date is in the past
        """
        if not (0 <= bundle_reduction <= 100):
            raise ValueError(
                "[BundleService] Cannot create bundle: Bundle reduction must be between 0 and 100."
            )

        if bundle_availability_start_date > bundle_availability_end_date:
            raise ValueError(
                "[BundleService] Cannot create bundle: Bundle end date must "
                "later than the start date"
            )

        today = datetime.now()
        if bundle_availability_end_date < today:
            raise ValueError(
                "[BundleService] Cannot update bundle: Start date cannot be in the past."
            )

        create_bundle = self.bundle_dao.create_bundle(
            bundle_name=bundle_name,
            bundle_reduction=bundle_reduction,
            bundle_description=bundle_description,
            bundle_availability_start_date=bundle_availability_start_date,
            bundle_availability_end_date=bundle_availability_end_date,
            bundle_items=bundle_items,
            bundle_image=bundle_image,
            is_in_menu=is_in_menu,
        )
        return create_bundle

    @log
    def update_bundle(self, bundle_id: int, update: dict) -> Bundle:
        """
        Update a bundle informations after checking infos from the dictionnary

        Checking:
            - The reduction percentage must be between 0 and 100
            - The ending availability date must be after the starting availability date
            - The starting availability date must be later than today

        Parameters
        ----------
        bundle_id : int
            Unique id of the bundle
        update : dict
            A dictionnary with the name of the variable to update as key and the change as value

        Returns
        -------
        Bundle
            The bundle if successfuly updated

        Raises
        ------
        ValueError
            If the dictionnary does not change anything
        ValueError
            Invalid starting date format
        ValueError
            Invalid ending date format
        ValueError
            If the ending availability date comes before the starting availability date
        ValueError
            If the starting availibility date is in the past
        ValueError
            If the reduction percentage isn't between 0 and 100
        """
        current_bundle = self.get_bundle_by_id(bundle_id)

        if all([value is None for value in update.values()]):
            raise ValueError(
                "[BundleService] Cannot update bundle: You must change at least one field."
            )

        start_date = None
        end_date = None

        if update.get("bundle_availability_start_date"):
            try:
                start_date = datetime.strptime(
                    update.get("bundle_availability_start_date"), "%d/%m/%Y"
                )
                update["bundle_availability_start_date"] = start_date
            except ValueError as e:
                raise ValueError(
                    "[BundleService] Cannot update bundle: Invalid start date format. "
                    "Expected format: DD/MM/YYYY"
                ) from e

        if update.get("bundle_availability_end_date"):
            try:
                end_date = datetime.strptime(update.get("bundle_availability_end_date"), "%d/%m/%Y")
                update["bundle_availability_end_date"] = end_date
            except (ValueError, TypeError) as e:
                raise ValueError(
                    "[BundleService] Cannot update bundle: Invalid end date format. "
                    "Expected format: DD/MM/YYYY"
                ) from e

        final_start_date = (
            start_date if start_date else current_bundle.bundle_availability_start_date
        )
        final_end_date = end_date if end_date else current_bundle.bundle_availability_end_date

        if final_end_date <= final_start_date:
            raise ValueError(
                "[BundleService] Cannot update bundle: End date "
                f"({final_end_date.strftime('%d/%m/%Y')}) must be after start date "
                f"({final_start_date.strftime('%d/%m/%Y')})."
            )

        today = datetime.now()
        if final_end_date < today:
            raise ValueError(
                "[BundleService] Cannot update bundle: Start date cannot be in the past."
            )

        if update.get("bundle_reduction") and not (0 <= update.get("bundle_reduction") <= 100):
            raise ValueError(
                "[BundleService] Cannot create bundle: Bundle reduction must be between 0 and 100."
            )

        update = {key: value for key, value in update.items() if update[key]}
        updated_bundle = self.bundle_dao.update_bundle(bundle_id=bundle_id, update=update)
        return updated_bundle

    @log
    def delete_bundle(self, bundle_id: int) -> None:
        """
        Deletes a bundle from the database by its id.

        Parameters
        ----------
        bundle_id : int
            The id of the bundle to delete.
        """
        self.get_bundle_by_id(bundle_id)
        self.bundle_dao.delete_bundle(bundle_id)
