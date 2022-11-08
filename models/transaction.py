from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from reportlab.graphics.renderbase import inverse


class TransactionOneDay(models.Model):
    _name = "transaction.oneday"
    _description = "All Transactions in One Day"
    # _rec_name="id"
    _order = "date_list_transaction"
    _sql_constraints = [('date_list_transaction_unique', 'unique(date_list_transaction)', "The date must be unique!")]
    
    name = fields.Char(string="Name Transaction One Day", compute="_compute_name", store=True, readonly=True)
    date_list_transaction = fields.Date(string='Date of Transaction One Day',default=fields.Date.today(), required=True , help="Date create list transaction")
    
    transaction_ids = fields.One2many('transaction', 'transaction_oneday_id', string="List Transaction")
    # wallet_ids = fields.Many2many('wallet', string='Wallets of Transaction One Day', 
    #     help="List wallet used for list transaction in transaction one day")
    
    # @api.onchange('date_list_transaction')
    # def _onchange_date_list_transaction(self):
    #     # print(self.transaction_ids)
    #     new_context = self.transaction_ids._context.copy()
    #     new_context.update({'date':self.date_list_transaction})
    #     self.transaction_ids.with_context(new_context)
    #     # self.env['transaction'].with_context(date = self.date_list_transaction)
    #     # return res
    
    @api.depends('date_list_transaction')
    def _compute_name(self):
        print(self)
        for r in self:
            if self.date_list_transaction:
                self.name = 'Transactions on ' + self.date_list_transaction.strftime("%B, %d %Y")
            
    @api.constrains('date_list_transaction')
    def constraint_date(self):
        # a = self.env['transaction.oneday'].browse(self.date_list_transaction).exists()
        # self.flush()
        # query="SELECT * FROM transaction_oneday t WHERE t.date_list_transaction = %s"
        # self.env.cr.execute(query, [self.date_list_transaction])
        # b = self._cr.fetchall()
        # print(b[0])
        # print(a.date_list_transaction)
        # print(self.date_list_transaction)
        # print(self.id)
        # print(a.id)
        # self.invalidate_cache()
        print(self)
        for r in self:
            if r.date_list_transaction:
                a = self.search([('date_list_transaction', '=', r.date_list_transaction)], count=True)
                if a > 1:
                    raise ValidationError("The date of transaction one day must be unique.")
            
        # self._cr.commit()
        
    def button_confirm(self):
        for r in self:
            print(r)


class Transaction(models.Model):
    _name = "transaction"
    _description = "Transaction of Transaction One Day"
    _rec_name = "category_id"
    _order = "date"
    
    # @api.model
    # def default_get(self, fields_list):
    #     # print(super.default_get(fields_list))
    #     # print(self)
    #     # if 'date' not in fields_list:
    #     #     return super().default_get(fields_list)
    #     # # print(fields_list)
    #     # default_date = self.env.context.get('date')
    #     # print(default_date)
    #     # new_context = self.with_context(default_date=default_date)
    #     print(self._context.get('date',False))
    #     return super(Transaction, self).default_get(fields_list)

    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        return self.env.company.currency_id

    @api.model
    def _referen_models(self):
        models = self.env['ir.model'].search([])
        return [(x.model, x.name) for x in models]
    
    balance = fields.Monetary(string='Balance of Transaction', currency_field='currency_id',
        groups='manager_money.group_user')
    
    date = fields.Datetime(string='Date of Transaction', copy=False, help="Date create this transaction", group_operator="count_distinct")
    type = fields.Selection(string='Type Transaction', selection=[('income', 'Income'), ('expense', 'Expense')], default='income')
    status = fields.Selection(string='Status Transaction', group_expand="_read_group_selection_field",
             readonly=False, selection=[('waiting_confirm', 'Waiting Confirm'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='draft')
    note = fields.Text(string='Note Transaction', compute="_compute_note",inverse="_inverse_note",  store=True, readonly=False, search="_search_note", translate=True)
     
    transaction_oneday_id = fields.Many2one('transaction.oneday', string='Transaction One Day ID', ondelete="cascade")
    wallet_id = fields.Many2one('wallet', string="Wallet")
    
    category_id = fields.Many2one('category', string='Category', ondelete='restrict')
    icon_category = fields.Html(string="Icon", related="category_id.embed_code", store=True, depends=['category_id'])
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=_get_default_currency)
    rate_money = fields.Float(string="Rate Money", related="currency_id.rate", store=True)
    
    res_model = fields.Char(string="res model")
    action = fields.Reference(selection='_referen_models', string='Reference', store=True)
    action_2 = fields.Many2oneReference(model_field='res.model', string="Many 2 one Reference", store=True)
    
    @api.model
    def _read_group_selection_field(self, values, domain, order):
        return ['draft', 'canceled', 'waiting_confirm', 'confirmed']
    
    # @api.model
    # def _group_expand(self): 
    #
    
    @api.model 
    def create(self, vals):
        if 'date' in vals and fields.Datetime.to_datetime(vals['date']) <= fields.Datetime.now():
           vals.update({'status': 'confirmed'})
        return super(Transaction, self).create(vals)
    
    # def write(self, vals):
    #     print(self._context)
    
    def _search_note(self, operator, value):
        if operator == 'like':
            operator = 'ilike'  
        return [('note', operator, value)]
    
    # @api.onchange('category_id')
    # def _onchange_note(self):
    #     if self[0].category_id:
    #         self.note = self.category_id.name
    #         # self.update({'note':self.category_id.name})
    #         # self.update({'note':'Testtttttt'})
    
    @api.depends('category_id')
    def _compute_note(self):
        for r in self:
            if r.category_id:
                r.note = r.category_id.name
            else:
                r.note = 'Default'
    
    def _inverse_note(self):
        print(self._fields)
        for r in self:
            if r.note:
                c = self.env['category'].sudo().search([('name','=',r.note)],limit=1)
                if c:
                    for s in c:
                        
                        r.category_id = getattr(s, 'id')
                else:
                    r.category_id = False
            else:
                r.category_id = False
            
    def button_confirm(self):
        for r in self:
            r.status = 'confirmed'
            
    @api.constrains('date')
    def _check_date(self):
        for r in self:
            if not r.transaction_oneday_id:
                return
            transaction_oneday = r.env['transaction.oneday'].browse(r.transaction_oneday_id.id)
            if self.filtered(lambda i: i.date and i.date.date() != transaction_oneday.date_list_transaction):
                raise ValidationError(_("The date transaction must be match with date of transaction one day."))
            
    def test_validate_cache(self):
        print(self)
        t_old = self.env['transaction'].search([('status', '=', 'draft')])
        print(t_old.read(['id', 'status']))
        self.update_transaction_state()
        t_new = self.env['transaction'].search([('status', '=', 'draft')])
        print(t_new.read(['id', 'status']))
    
    # update all transactions have state is draft and transaction have wallet is active
    def update_transaction_state(self):
        print(self._context)
        # đẩy tất cả tính toán liên quan đến table transaction vào db
        self.env['transaction'].flush(self.env['transaction']._fields)
        query = """
            WITH relation AS(
                SELECT t.id,t.status,t.date FROM transaction t 
                    LEFT JOIN wallet w ON w.id = t.wallet_id
                    LEFT JOIN transaction_oneday td ON td.id = t.transaction_oneday_id
                    WHERE t.status = %s
                        AND t.date < now() 
                    ORDER BY t.date
                    LIMIT 2
            )
            UPDATE transaction
            SET status = %s
            FROM relation
            WHERE transaction.id = relation.id 
        """
        self.env.cr.execute(query, ['draft', 'canceled'])
        # Xoá cache cũ sau khi cập nhật db để khi request data sau đó không bị cache cũ
        self.env['transaction'].invalidate_cache(self.env['transaction']._fields)

    @api.model
    def _autotransactions_draft_entries(self):
        'This method is called from a cron job.'
        time = timedelta(minutes=1)
        transactions_daft = self.search([
            ('date', '>=', fields.Datetime.now() - time),
            ('status', '=', 'draft'),
        ])

        if transactions_daft:
            for t in transactions_daft:
                delta = t.date - fields.Datetime.now()
                if delta < time:
                    t.write({'status':'waiting_confirm'})
                    
        transactions_waiting = self.search([
            ('status', '=', 'waiting_confirm'),
        ])
        
        if transactions_waiting:
            for t in transactions_waiting:
                if fields.Datetime.now() - t.date >= time:
                    t.write({'status':'canceled'})
       
        # for ids in self._cr.split_for_in_conditions(transactions.ids, size=1000):
        #     self.browse(ids)._post()
        #     if not self.env.registry.in_test_mode():
        #         self._cr.commit()


class ImageExtend(models.AbstractModel):
    _name = "image.extend"
    _inherit = ['image.mixin']
    _description = "Extend model image mixin"
    
    image_64 = fields.Image("Image 64", related="image_1920", max_width=64, max_height=64)
    image_32 = fields.Image("Image 32", related="image_1920", max_width=32, max_height=32)
    image_24 = fields.Image("Image 24", related="image_1920", max_width=24, max_height=24)


class TransactionExtend(models.Model):
    _name = "transaction"
    _inherit = ['transaction', 'image.extend']
    
    attachment_binary = fields.Binary(string="Attachment Transaction Binary", related='image_1920', store=True, readonly=False, attachment=False, prefetch=False)
    attachment_image = fields.Image(string="Attachment Transaction Image", related='image_1920', store=True, readonly=False, verify_resolution=True)
    status = fields.Selection(selection_add=[('draft', 'Draft')], ondelete={'draft':'cascade'})
    type = fields.Selection(selection_add=[('test', 'Test')], ondelete={'test':'set default'})
