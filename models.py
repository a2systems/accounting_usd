from odoo import tools, models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date,datetime


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            for line in rec.line_ids:
                #                    amount = line.company_currency_id._convert(
                #        abs(line.amount_residual),
                #        move.currency_id,
                #        move.company_id,
                #        line.date,
                #    )
                if line.move_id.currency_id.id == self.env.ref('base.USD').id:
                    line.debit_usd = line.debit
                    line.credit_usd = line.credit
                else:
                    line.debit_usd = line.move_id.currency_id._convert(
                        line.debit,
                        self.env.ref('base.USD'),
                        line.company_id,
                        line.date,
                    )
                    line.credit_usd = line.move_id.currency_id._convert(
                        line.credit,
                        self.env.ref('base.USD'),
                        line.company_id,
                        line.date,
                    )

        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    debit_usd = fields.Float('Debito USD')
    credit_usd = fields.Float('Credito USD')
