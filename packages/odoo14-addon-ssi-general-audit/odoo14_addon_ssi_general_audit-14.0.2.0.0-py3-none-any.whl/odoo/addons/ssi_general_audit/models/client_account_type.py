# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class ClientAccountType(models.Model):
    _name = "client_account_type"
    _inherit = ["mixin.master_data"]
    _description = "Client Account Type"
    _order = "sequence, id"
    _show_code_on_display_name = True

    group_id = fields.Many2one(
        string="Client Account Group",
        comodel_name="client_account_group",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    normal_balance = fields.Selection(
        string="Normal Balance",
        selection=[
            ("dr", "Debit"),
            ("cr", "Credit"),
        ],
        required=True,
        default="dr",
    )
    python_code = fields.Text(
        string="Python Code",
        required=True,
        default="result = document.balance",
    )
