# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockPickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ["stock.picking.type"]

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
    )
    debit_account_method = fields.Selection(
        string="Debit Account Method",
        selection=[
            ("manual", "Manual"),
            ("code", "Python Code"),
        ],
    )
    debit_usage_id = fields.Many2one(
        string="Debit Usage",
        comodel_name="product.usage_type",
        ondelete="restrict",
    )
    debit_account_code = fields.Text(
        string="Debit Account Python Code",
    )

    credit_account_method = fields.Selection(
        string="Credit Account Method",
        selection=[
            ("manual", "Manual"),
            ("code", "Python Code"),
        ],
    )
    credit_usage_id = fields.Many2one(
        string="Credit Usage",
        comodel_name="product.usage_type",
        ondelete="restrict",
    )
    credit_account_code = fields.Text(
        string="Credit Account Python Code",
    )
