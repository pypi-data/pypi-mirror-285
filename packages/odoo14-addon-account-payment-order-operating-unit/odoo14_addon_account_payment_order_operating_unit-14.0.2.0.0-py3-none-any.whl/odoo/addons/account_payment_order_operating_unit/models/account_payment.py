
from odoo import api, models, fields
from odoo.tools.translate import _


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    def move_line_offsetting_account_hashcode(self):
        """
        This method is inherited in the module
        account_banking_sepa_direct_debit
        https://github.com/OCA/bank-payment/blob/12.0/account_banking_sepa_direct_debit/models/bank_payment_line.py
        """
        self.ensure_one()
        if self.order_id.payment_mode_id.move_option == 'date':
            hashcode = fields.Date.to_string(self.date)
        else:
            hashcode = str(self.id)
        return hashcode

    @api.depends("journal_id")
    def _compute_operating_unit_id(self):
        for payment in self:
            if payment.operating_unit_id:
                continue
            elif payment.journal_id:
                payment.operating_unit_id = payment.journal_id.operating_unit_id