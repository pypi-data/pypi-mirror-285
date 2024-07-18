import base64
from odoo.tests import common


class IrAttachmentTestCase(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_10")

    def content_base64(self):
        return base64.b64encode(b"\xff data")

    def test_create_attachment(self):
        self.env["ir.attachment"].create(
            {
                "name": "Test file",
                "res_model": self.partner._name,
                "res_id": self.partner.id,
                "datas": self.content_base64(),
            }
        )
        directory = self.env["dms.directory"].search(
            [
                ("res_id", "=", self.partner.id),
                ("res_model", "=", self.partner._name),
                ("name", "=", f"{self.partner.vat} - {self.partner.name}"),
            ]
        )

        assert directory
