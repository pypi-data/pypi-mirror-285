from odoo.exceptions import ValidationError
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo import _
import logging

from . import schemas

_logger = logging.getLogger(__name__)


class DMSFileAPIService(Component):
    _name = "dms.file.api.service"
    _inherit = "base.rest.service"
    _collection = "api_common_base.services"
    _usage = "documentation"
    _description = """
        DMS API
        Create dms files
    """

    @restapi.method(
        [(["/"], "POST")],
        input_param=restapi.CerberusValidator(schemas.S_DMS_FILE_CREATE),
        output_param=restapi.CerberusValidator(schemas.LIST_IDS_SCHEMA),
    )
    def create_file(self, **params):
        file_params = self._prepare_create(params)

        dms_ids = []
        for file in params["files"]:
            file_params.update(
                {
                    "name": file["filename"],
                    "content": file["content"],
                }
            )
            dms = self.env["dms.file"].create(file_params)
            dms_ids.append(dms.id)

        result = {"ids": dms_ids}

        _logger.debug(result)

        return result

    def _prepare_create(self, params):
        if params.get("crm_lead_id"):
            res_model = "crm.lead"
            res_id = params["crm_lead_id"]
        else:
            res_model = "res.partner"
            partner = self.env[res_model].search([("ref", "=", params["partner_ref"])])
            if not partner:
                error_msg = _("Partner with ref: {} not found in our system")
                raise ValidationError(error_msg.format(params["partner_ref"]))
            res_id = partner.id

        category = self.env["dms.category"].search([("code", "=", params["category"])])
        if not category:
            error_msg = _("Category with code: {} not found in our system")
            raise ValidationError(error_msg.format(params["category"]))

        root_directory = self.env["dms.directory"].search(
            [
                ("res_model", "=", res_model),
                ("category_id", "in", category.get_all_parent_categories().ids),
                ("is_root_directory", "=", True),
            ],
            limit=1,
        )
        if not root_directory:
            error_msg = _(
                "Root directory with with category {} and model {} not found in our system"  # noqa
            )
            raise ValidationError(error_msg.format(category.code, res_model))

        return {
            "res_model": res_model,
            "res_id": int(res_id),
            "category_id": category.id if category else None,
            "root_directory_id": root_directory.id,
        }
