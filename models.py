from odoo import tools, models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date,datetime

class AccountAccount(models.Model):
    _inherit = "account.account"

    def _compute_balance_usd(self):
        for rec in self:
            res = 0
            sql = "select sum(coalesce(debit_usd,0) - coalesce(credit_usd,0)) as balance_usd from account_move_line where account_id = %s and company_id = %s"%(rec.id,rec.company_id.id)
            self.env.cr.execute(sql)
            result = self.env.cr.fetchall()
            if result:
                res = result[0][0]
            rec.balance_usd = res

    balance_usd = fields.Float('Saldo USD',compute=_compute_balance_usd)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            for line in rec.line_ids:
                if line.move_id.currency_id.id == self.env.ref('base.USD').id:
                    line.debit_usd = line.debit
                    line.credit_usd = line.credit
                else:
                    line.debit_usd = line.move_id.currency_id.with_context(force_company=line.move_id.company_id.id)._convert(
                        line.debit,
                        self.env.ref('base.USD'),
                        line.company_id,
                        line.date,
                    )
                    line.credit_usd = line.move_id.currency_id.with_context(force_company=line.move_id.company_id.id)._convert(
                        line.credit,
                        self.env.ref('base.USD'),
                        line.company_id,
                        line.date,
                    )

        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_usd_rate(self):
        for rec in self:
            res = 0
            if rec.debit_usd > 0:
                res = rec.debit / rec.debit_usd
            if rec.credit_usd > 0:
                res = rec.credit / rec.credit_usd
            rec.usd_rate = res

    def _compute_balance_usd(self):
        for rec in self:
            res = rec.debit_usd - rec.credit_usd
            rec.balance_usd = res

    def _compute_running_balance_usd(self):
        for rec in self:
            res = 0
            sql = "select sum(coalesce(debit_usd,0) - coalesce(credit_usd,0)) as balance_usd from account_move_line where account_id = %s and date <= '%s' and id <= %s and company_id = %s"%(rec.account_id.id,rec.date,rec.id,rec.company_id.id)
            self.env.cr.execute(sql)
            result = self.env.cr.fetchall()
            if result:
                res = result[0][0]
            rec.running_balance_usd = res


    debit_usd = fields.Float('Debito USD')
    credit_usd = fields.Float('Credito USD')
    usd_rate = fields.Float('Tipo de cambio USD',compute=_compute_usd_rate)
    balance_usd = fields.Float('Saldo USD',compute=_compute_balance_usd)
    running_balance_usd = fields.Float('Saldo a la Fecha USD',compute=_compute_running_balance_usd)
