from odoo import fields, models


class TransactionOnedayWizard(models.Model):
    _name = "transaction.oneday.wizard"
    _description = "Duplicate transaction one day"
    
    date_new_transaction = fields.Date(string="Date of new transaction one day", default=fields.Date.today())
    
    def duplicate_transaction_oneday(self):
        self.ensure_one()
        for r in self:
            transaction_oneday = self.env['transaction.oneday'].browse(self.env.context['active_ids']).exists()
            for t in transaction_oneday:
                t.copy({'name':'Transactions on ' + r.date_new_transaction.strftime("%B, %d %Y"), 'date_list_transaction':r.date_new_transaction})