from odoo import fields, models, api

class TransactionWizard(models.TransientModel):
    _name = "transaction.wizard"
    _description = "Update multi transaction"
    # _log_access = True
    
    wallet_id = fields.Many2one('wallet', string ="Wallet ID")
    
    def update_multi_transaction(self):
        transactions = self.env['transaction'].browse(self.env.context['active_ids'])
        new_data = {}
        print(self)
        if self.wallet_id:
            new_data['wallet_id'] = self.wallet_id
        transactions.write(new_data)