from odoo.addons.base_rest.controllers.main import RestController


class DMSFileController(RestController):
    _root_path = "/api/"
    _collection_name = "dms.file.services"
    _default_auth = "api_key"
