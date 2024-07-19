# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ChangePickingActualMovementDate(models.TransientModel):
    _name = "change_picking_actual_movement_date"
    _inherit = "change_picking_actual_movement_date"
    _description = "Change Picking Actual Movement Date"

    def _confirm(self):
        _super = super(ChangePickingActualMovementDate, self)
        _super._confirm()
        self._update_svl_actual_movement_date()

    def _update_svl_actual_movement_date(self):
        self.ensure_one()
        if len(self.picking_ids.stock_valuation_layer_ids) > 0:
            query = """
                UPDATE public.stock_valuation_layer
                    SET create_date = %(create_date)s
                WHERE id IN %(svl_ids)s
            """
            params = {
                "create_date": self.actual_movement_date,
                "svl_ids": tuple(self.picking_ids.stock_valuation_layer_ids.ids),
            }
            self._cr.execute(query, params)
