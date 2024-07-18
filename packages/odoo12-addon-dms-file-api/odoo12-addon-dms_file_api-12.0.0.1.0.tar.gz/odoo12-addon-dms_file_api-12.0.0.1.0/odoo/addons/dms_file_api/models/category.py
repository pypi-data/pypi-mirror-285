# -*- coding: utf-8 -*-

from odoo import models, fields


class Category(models.Model):
    _inherit = "dms.category"

    code = fields.Char(string="code")

    def get_all_parent_categories(self):
        self.ensure_one()

        categories = self.browse()
        current_category = self

        while current_category:
            categories |= current_category
            current_category = current_category.parent_id

        return categories
