from odoo import fields, models, api
from odoo.tools.translate import _


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    operating_unit_ids = fields.One2many(
        comodel_name="operating.unit",
        compute="_get_operating_unit_ids",
        store=False
    )

    @api.depends('payment_line_ids')
    def _get_operating_unit_ids(self):
        operating_units = {}
        vals = []
        for record in self:
            for payment_line in record.payment_line_ids:
                operating_units[
                    payment_line.operating_unit_id.id
                ] = payment_line.operating_unit_id.id
            for operating_unit_id in operating_units.keys():
                vals.append(operating_unit_id)
            record.operating_unit_ids = vals