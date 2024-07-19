
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    # We overwrite again this method because we want to avoid behaviour
    # defined on account_banking_sepa_direct_debit
    def move_line_offsetting_account_hashcode(self):
        """
        This method is inherited in the module
        account_banking_sepa_direct_debit
        """
        self.ensure_one()
        if self.order_id.payment_mode_id.move_option == 'date':
            hashcode = fields.Date.to_string(self.date)
        else:
            hashcode = str(self.id)
        return hashcode

    def reconcile(self):
        self.ensure_one()
        # reconcile based on operating unit
        for operating_unit in self.order_id.operating_unit_ids:
            transit_mlines = self.env[
                'account.move.line'
            ].search([
                ('bank_payment_line_id', '=', self.id),
                ('operating_unit_id', '=', operating_unit.id)
            ])
            if transit_mlines.exists():
                assert len(transit_mlines) == 1, 'We should have only 1 move'
                transit_mline = transit_mlines[0]
                assert not transit_mline.reconciled,\
                    'Transit move should not be reconciled'
                lines_to_rec = transit_mline
                for payment_line in self.payment_line_ids:
                    # from related payment lines get only the ones with same operating unit
                    if payment_line.operating_unit_id.id == operating_unit.id:
                        if not payment_line.move_line_id:
                            raise UserError(_(
                                "Can not reconcile: no move line for "
                                "payment line %s of partner '%s'.") % (
                                    payment_line.name,
                                    payment_line.partner_id.name))
                        if payment_line.move_line_id.reconciled:
                            raise UserError(_(
                                "Move line '%s' of partner '%s' has already "
                                "been reconciled") % (
                                    str(payment_line.move_line_id.id),
                                    payment_line.partner_id.name))
                        if (
                                payment_line.move_line_id.account_id !=
                                transit_mline.account_id):
                            raise UserError(_(
                                "For partner '%s', the account of the account "
                                "move line to pay (%s) is different from the "
                                "account of of the transit move line (%s).") % (
                                    payment_line.move_line_id.partner_id.name,
                                    payment_line.move_line_id.account_id.code,
                                    transit_mline.account_id.code))
                        lines_to_rec += payment_line.move_line_id
                lines_to_rec.reconcile()
