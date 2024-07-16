# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = ["stock.location"]

    def _should_be_valued(self):
        _super = super(StockLocation, self)

        result = _super._should_be_valued()

        if not result and self.env.context.get("bypass_location_restriction", False):
            result = True

        return result
