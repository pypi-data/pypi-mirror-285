# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _name = "stock.valuation.layer"
    _inherit = [
        "stock.valuation.layer",
        "mixin.account_move",
        "mixin.account_move_double_line",
        "mixin.company_currency",
    ]
    # account.move.line
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "account_move_id"
    _accounting_date_field_name = "date"  # TODO
    _currency_id_field_name = "company_currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _number_field_name = False

    # Debit ML Attribute
    _debit_account_id_field_name = "debit_account_id"
    _debit_partner_id_field_name = "partner_id"
    _debit_analytic_account_id_field_name = "analytic_account_id"
    _debit_label_field_name = "description"
    _debit_product_id_field_name = "product_id"
    _debit_uom_id_field_name = "uom_id"
    _debit_quantity_field_name = "quantity"
    _debit_price_unit_field_name = "unit_cost"
    _debit_currency_id_field_name = "company_currency_id"
    _debit_company_currency_id_field_name = "company_currency_id"
    _debit_amount_currency_field_name = "value"
    _debit_company_id_field_name = "company_id"
    _debit_date_field_name = "date"
    _debit_need_date_due = False
    _debit_date_due_field_name = False

    # Credit ML Attribute
    _credit_account_id_field_name = "credit_account_id"
    _credit_partner_id_field_name = "partner_id"
    _credit_analytic_account_id_field_name = "analytic_account_id"
    _credit_label_field_name = "description"
    _credit_product_id_field_name = "product_id"
    _credit_uom_id_field_name = "uom_id"
    _credit_quantity_field_name = "quantity"
    _credit_price_unit_field_name = "unit_cost"
    _credit_currency_id_field_name = "company_currency_id"
    _credit_company_currency_id_field_name = "company_currency_id"
    _credit_amount_currency_field_name = "value"
    _credit_company_id_field_name = "company_id"
    _credit_date_field_name = "date"
    _credit_need_date_due = False
    _credit_date_due_field_name = False

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        related=False,
        compute="_compute_journal_id",
        store=False,
        readonly=False,
    )
    debit_account_id = fields.Many2one(
        string="Debit Account",
        related="stock_move_id.debit_account_id",
        readonly=False,
    )
    credit_account_id = fields.Many2one(
        string="Credit Account",
        related="stock_move_id.credit_account_id",
        readonly=False,
    )
    analytic_account_id = fields.Many2one(
        related="stock_move_id.analytic_account_id",
        readonly=False,
    )
    partner_id = fields.Many2one(
        string="Partner",
        related="stock_move_id.picking_id.partner_id",
        readonly=False,
    )
    date = fields.Date(
        string="Date",
        compute="_compute_date",
        store=True,
    )
    debit_move_line_id = fields.Many2one(
        string="Debit Move Line",
        comodel_name="account.move.line",
        readonly=False,
    )
    credit_move_line_id = fields.Many2one(
        string="Credit Move Line",
        comodel_name="account.move.line",
        readonly=False,
    )

    def _compute_journal_id(self):
        for record in self:
            journal = False
            if (
                record.stock_move_id.picking_id
                and record.stock_move_id.picking_id.journal_id
            ):
                journal = record.stock_move_id.picking_id.journal_id.id
            elif record.stock_move_id.picking_type_id.journal_id:
                journal = record.stock_move_id.picking_type_id.journal_id.id
            record.journal_id = journal

    @api.depends("create_date")
    def _compute_date(self):
        for record in self:
            record.date = fields.Date.to_date(record.create_date)

    def action_create_accounting_entry(self):
        for record in self.sudo():
            record._create_accounting_entry()

    def action_delete_accounting_entry(self):
        for record in self.sudo():
            record._delete_accounting_entry()

    def _create_accounting_entry(self):
        if self.account_move_id:
            return True

        self._create_standard_move()  # Mixin
        debit_ml, credit_ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "debit_move_line_id": debit_ml.id,
                "credit_move_line_id": credit_ml.id,
            }
        )
        self.account_move_id.write(
            {
                "stock_move_id": self.stock_move_id.id,
            }
        )
        self._post_standard_move()  # Mixin

    def _delete_accounting_entry(self):
        self.ensure_one()
        self._delete_standard_move()  # Mixin
