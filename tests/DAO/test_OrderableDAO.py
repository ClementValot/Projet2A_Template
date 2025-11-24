class TestOrderableDAO:
    def test_create_orderable_item(self, orderable_dao, clean_database):
        orderable_id = orderable_dao.create_orderable("item", "test")

        assert orderable_id is not None
        assert isinstance(orderable_id, int)
        assert orderable_id > 0

    def test_create_orderable_bundle(self, orderable_dao, clean_database):
        orderable_id = orderable_dao.create_orderable("bundle", "test")

        assert orderable_id is not None
        assert isinstance(orderable_id, int)
        assert orderable_id > 0

    def test_create_multiple_orderables(self, orderable_dao, clean_database):
        id1 = orderable_dao.create_orderable("item", "test")
        id2 = orderable_dao.create_orderable("bundle", "test")
        id3 = orderable_dao.create_orderable("item", "test")

        assert id1 != id2 != id3
        assert id1 < id2 < id3

    def test_create_orderables_with_image(self, orderable_dao, clean_database):
        orderable_dao.create_orderable("bundle", "test", "")
        # Todo

    def test_get_orderable_by_id_exist(
        self, orderable_dao, sample_bundle, sample_item, clean_database
    ):
        bundle_id = orderable_dao.get_orderable_by_id(sample_bundle.bundle_id)
        item_id = orderable_dao.get_orderable_by_id(sample_item.item_id)

        assert bundle_id is not None
        assert item_id is not None

    def test_get_all_orderables_empty(self, orderable_dao, clean_database):
        """Test getting all orderables when there are none"""
        orderables = orderable_dao.get_all_orderables()

        assert orderables == []

    def test_get_all_orderables_multiple(self, orderable_dao, clean_database):
        """Test getting all orderables"""
        orderable_dao.create_orderable("item", "test", is_in_menu=True)
        orderable_dao.create_orderable("bundle", "test", is_in_menu=False)
        orderable_dao.create_orderable("item", "test", is_in_menu=True)

        orderables = orderable_dao.get_all_orderables()

        assert orderables is not None
        assert len(orderables) == 3

    def test_update_orderable_state_to_true(self, orderable_dao, clean_database):
        """Test updating orderable state from False to True"""
        orderable_id = orderable_dao.create_orderable("item", "test", is_in_menu=False)

        updated_orderable = orderable_dao.update_orderable_state(orderable_id, True)

        assert updated_orderable is not None
        assert updated_orderable["is_in_menu"] is True

    def test_update_orderable_state_to_false(self, orderable_dao, clean_database):
        """Test updating orderable state from True to False"""
        orderable_id = orderable_dao.create_orderable("bundle", "test", is_in_menu=True)

        updated_orderable = orderable_dao.update_orderable_state(orderable_id, False)

        assert updated_orderable is not None
        assert updated_orderable["is_in_menu"] is False

    def test_is_in_menu_true(self, orderable_dao, clean_database):
        """Test _is_in_menu returns True for orderable in menu"""
        orderable_id = orderable_dao.create_orderable("item", "test", is_in_menu=True)

        is_in_menu = orderable_dao._is_in_menu(orderable_id)

        assert is_in_menu is True

    def test_is_in_menu_false(self, orderable_dao, clean_database):
        """Test _is_in_menu returns False for orderable not in menu"""
        orderable_id = orderable_dao.create_orderable("item", "test", is_in_menu=False)

        is_in_menu = orderable_dao._is_in_menu(orderable_id)

        assert is_in_menu is False

    def test_is_in_menu_not_exists(self, orderable_dao, clean_database):
        """Test _is_in_menu returns None for non-existing orderable"""
        is_in_menu = orderable_dao._is_in_menu(9999)

        assert is_in_menu is None
