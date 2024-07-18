from odoo.tests.common import TransactionCase


class TestDMSCategory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.insurance_category = self.env.ref(
            "dms_res_model_root_directory.category_insurances_data"
        )
        self.id_category = self.env.ref("dms_res_model_root_directory.category_id_data")

    def test_get_all_parent_categories_no_parent(self):
        parent_categories = self.insurance_category.get_all_parent_categories()

        assert len(parent_categories) == 1
        assert self.insurance_category == parent_categories

    def test_get_all_parent_categories_with_parents(self):
        root_category = self.env["dms.category"].create(
            {
                "name": "Category Root",
                "code": "category_1",
            }
        )
        self.insurance_category.parent_id = self.id_category
        self.id_category.parent_id = root_category

        parent_categories = self.insurance_category.get_all_parent_categories()

        assert len(parent_categories) == 3
        assert root_category in parent_categories
        assert self.id_category in parent_categories
        assert self.insurance_category in parent_categories
