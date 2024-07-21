# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class GeneralAuditWorksheetConclusion(models.Model):
    _name = "general_audit_worksheet_conclusion"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "General Audit Worksheet Conclusion"
    _order = "type_id, sequence, code"

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="general_audit_worksheet_type",
        required=True,
    )
