# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Inventory + Accounting Integration",
    "version": "14.0.2.11.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "ssi_stock",
        "ssi_financial_accounting",
        "stock_account",
        "ssi_accounting_entry_mixin",
        "ssi_company_currency_mixin",
        "ssi_product_usage_account_type",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "views/stock_valuation_layer_views.xml",
    ],
    "demo": [],
}
