# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

import base64
import csv
import io

from odoo import api, fields, models


class ImportClientAccount(models.TransientModel):
    _name = "import_client_account"
    _description = "Import Client Account"

    @api.model
    def _default_client_account_mapping(self):
        return self.env.context.get("active_id", False)

    mapping_id = fields.Many2one(
        string="# Client Account Mapping",
        comodel_name="client_account_mapping",
        default=lambda self: self._default_client_account_mapping(),
    )
    data = fields.Binary(string="File", required=True)

    def button_import(self):
        self.ensure_one()
        csv_data = base64.b64decode(self.data)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        reader = csv.reader(data_file, delimiter=",")
        for row in reader:
            self._import_client_account(row)
        return {"type": "ir.actions.act_window_close"}

    def _import_client_account(self, row):
        self.ensure_one()
        Account = self.env["client_account"]
        criteria = [
            ("partner_id", "=", self.mapping_id.partner_id.id),
            ("code", "=", row[0]),
        ]
        accounts = Account.search(criteria)
        if len(accounts) > 0:
            account = accounts[0]
        else:
            account = Account.create(
                {
                    "code": row[0],
                    "name": row[1],
                    "partner_id": self.mapping_id.partner_id.id,
                }
            )

        criteria = [
            ("account_id", "=", account.id),
            ("mapping_id", "=", self.mapping_id.id),
        ]
        details = self.env["client_account_mapping.detail"].search(criteria)

        if len(details) == 0:
            self.env["client_account_mapping.detail"].create(
                {
                    "mapping_id": self.mapping_id.id,
                    "account_id": account.id,
                }
            )
