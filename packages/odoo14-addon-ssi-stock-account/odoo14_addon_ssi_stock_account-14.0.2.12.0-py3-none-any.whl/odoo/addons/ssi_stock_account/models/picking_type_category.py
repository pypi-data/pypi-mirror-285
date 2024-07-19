# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class PickingTypeCategory(models.Model):
    _name = "picking_type_category"
    _inherit = ["picking_type_category"]

    # Debit Account
    debit_account_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Debit Account Selection Method",
        required=True,
    )
    debit_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="rel_picking_type_category_2_debit_account",
        column1="category_id",
        column2="account_id",
        string="Debit Accounts",
    )
    debit_account_domain = fields.Text(default="[]", string="Product Domain")
    debit_account_python_code = fields.Text(
        default="result = []", string="Debit Account Python Code"
    )

    # Credit Account
    credit_account_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Credit Account Selection Method",
        required=True,
    )
    credit_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="rel_picking_type_category_2_credit_account",
        column1="category_id",
        column2="account_id",
        string="Credit Accounts",
    )
    credit_account_domain = fields.Text(default="[]", string="Product Domain")
    credit_account_python_code = fields.Text(
        default="result = []", string="Credit Account Python Code"
    )
