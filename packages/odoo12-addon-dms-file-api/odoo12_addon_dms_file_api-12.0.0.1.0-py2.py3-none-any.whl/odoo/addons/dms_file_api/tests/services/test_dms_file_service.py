import base64
import json
import odoo
import requests
from pathlib import Path
from odoo.addons.api_common_base.tests.common_service import APICommonBaseRestCase


class TestDMSFileController(APICommonBaseRestCase):
    def setUp(self):
        super().setUp()
        self.session = requests.Session()
        self.DMSFile = self.env["dms.file"]
        self.category = self.env.ref("dms_res_model_root_directory.category_id_data")
        self.url = "/api/documentation"
        self.partner = self.env.ref("base.res_partner_2")
        self.partner.ref = "1234"
        self.crm_lead = self.env["crm.lead"].create(
            {
                "name": "Test Lead",
                "partner_id": self.partner.id,
            }
        )
        # File entry
        module_path = Path(__file__).resolve().parents[2]
        file_name = "icon.png"
        relative_path = "static/description/"
        file_path = module_path / relative_path / file_name
        file = open(file_path, "rb")
        file_content = base64.b64encode(file.read()).decode("utf-8")

        self.dms_file_params = {
            "partner_ref": self.partner.ref,
            "category": self.category.code,
            "files": [
                {
                    "filename": file_name,
                    "content": file_content,
                }
            ],
        }

    def test_create_dms_file_partner(self):
        """
        Test DMS File creation by API to a partner
        """

        response = self.http_post(self.url, self.dms_file_params)
        assert response.status_code == 200

        content = json.loads(response.content.decode("utf-8"))
        assert "ids" in content

        dms_file = self.DMSFile.browse(content["ids"][0])
        assert dms_file

        assert dms_file.res_id == self.partner.id
        assert dms_file.res_model == self.partner._name
        assert dms_file.directory_id.res_id == dms_file.res_id
        assert dms_file.directory_id.res_model == dms_file.res_model
        assert dms_file.directory_id.parent_id == self.env.ref(
            "dms_res_model_root_directory.id_data_directory"
        )

    def test_create_dms_file_child_category(self):
        """
        Test DMS File creation by API with a category
        child of the root directory category
        """
        test_category = self.env["dms.category"].create(
            {
                "name": "Test category",
                "code": "test",
                "parent_id": self.category.id,
            }
        )
        self.dms_file_params["category"] = test_category.code

        response = self.http_post(self.url, self.dms_file_params)

        assert response.status_code == 200

        content = json.loads(response.content.decode("utf-8"))
        assert "ids" in content

        dms_file = self.DMSFile.browse(content["ids"][0])
        assert dms_file
        assert dms_file.directory_id.parent_id == self.env.ref(
            "dms_res_model_root_directory.id_data_directory"
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_create_dms_file_partner_not_found(self):
        """
        Test DMS File creation by API to a non existing partner
        """

        self.partner.ref = False

        response = self.http_post(self.url, self.dms_file_params)

        assert response.status_code == 400  # ValidationError
        assert response.reason == "BAD REQUEST"

        content = json.loads(response.content.decode("utf-8"))

        error_msg = "Partner with ref: {} not found in our system".format(
            self.dms_file_params["partner_ref"]
        )
        assert error_msg in content["description"]

    def test_create_dms_file_crm_lead(self):
        """
        Test DMS File creation by API to a crm lead
        """
        dms_file_params = {
            "crm_lead_id": self.crm_lead.id,
            "category": self.category.code,
            "files": self.dms_file_params["files"],
        }
        crm_root_directory = self.env["dms.directory"].create(
            {
                "name": "crm insurances",
                "is_root_directory": True,
                "root_storage_id": self.env.ref("dms.storage_attachment_demo").id,
                "category_id": self.category.id,
                "model_id": self.env.ref("crm.model_crm_lead").id,
            }
        )

        response = self.http_post(self.url, dms_file_params)
        assert response.status_code == 200

        content = json.loads(response.content.decode("utf-8"))
        assert "ids" in content

        dms_file = self.DMSFile.browse(content["ids"][0])
        assert dms_file

        assert dms_file.res_id == self.crm_lead.id
        assert dms_file.res_model == self.crm_lead._name
        assert dms_file.directory_id.res_id == dms_file.res_id
        assert dms_file.directory_id.res_model == dms_file.res_model
        assert dms_file.directory_id.parent_id == crm_root_directory

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_create_dms_file_wo_file(self):
        """
        Test DMS File creation by API without any file
        """
        dms_file_params = {
            "crm_lead_id": self.crm_lead.id,
            "category": self.category.code,
        }

        response = self.http_post(self.url, dms_file_params)

        assert response.status_code == 400
        assert response.reason == "BAD REQUEST"

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_create_dms_file_wrong_category(self):
        """
        Test DMS File creation by API with wrong category
        """
        self.dms_file_params["category"] = "empty"

        response = self.http_post(self.url, self.dms_file_params)

        assert response.status_code == 400  # ValidationError
        assert response.reason == "BAD REQUEST"

        content = json.loads(response.content.decode("utf-8"))

        error_msg = "Category with code: {} not found in our system".format(
            self.dms_file_params["category"]
        )
        assert error_msg in content["description"]

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_create_dms_file_no_root_directory(self):
        """
        Test DMS File creation by API with category
        not related to root directory
        """
        test_category = self.env["dms.category"].create(
            {
                "name": "Test category",
                "code": "test",
            }
        )
        self.dms_file_params["category"] = test_category.code

        response = self.http_post(self.url, self.dms_file_params)

        assert response.status_code == 400  # ValidationError
        assert response.reason == "BAD REQUEST"

        content = json.loads(response.content.decode("utf-8"))

        error_msg = "Root directory with with category {} and model {}".format(
            test_category.code, "res.partner"
        )
        assert error_msg in content["description"]
