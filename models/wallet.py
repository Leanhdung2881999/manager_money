from odoo import fields, models, api
import time
from datetime import datetime, date


class Wallet(models.Model):
    _name = 'wallet'
    _description = 'Wallet'
    _sql_constraints = [('name_unique', 'unique(name)', "The name wallet must be unique!")]
    _rec_name = "name"
    
    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        return self.env.company.currency_id
    
    name = fields.Char(string='Name Wallet', required=True, index=True, translate=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft', readonly=True)
    start_balance = fields.Monetary(string="Start Balance", currency_field='currency_id', groups='manager_money.group_user')
    total_income = fields.Monetary(string='Total Income', store=True,
        compute='_compute_total_balance', currency_field='currency_id')
    total_expense = fields.Monetary(string='Total Expense', store=True,
        compute='_compute_total_balance', currency_field='currency_id')
    total = fields.Monetary(string="Total", compute='_compute_total_balance', currency_field='currency_id', compute_sudo=True, groups='manager_money.group_user')
    profited = fields.Boolean(compute='_compute_total_balance', default=True, compute_sudo=True)
    active = fields.Boolean(string="Wallet Private", default=True, readonly=True)
    transaction_count = fields.Integer(string="Transaction Count", compute='_compute_transaction_count')
    test = fields.Float(digits=(4, 3))
    
    transaction_ids = fields.One2many('transaction', 'wallet_id', string='List Transactions')
    currency_id = fields.Many2one('res.currency', string='Currency', default=_get_default_currency)
    
    @api.depends('transaction_ids', 'start_balance')
    def _compute_total_balance(self):
        # print('day la: %s' % self._context)
        for r in self:
            if r.transaction_ids:
                r.total_income = sum(r.transaction_ids.filtered(lambda t: t.type == 'income' and t.status == 'confirmed').mapped('balance'))
                r.total_expense = sum(r.transaction_ids.filtered(lambda t: t.type == 'expense'and t.status == 'confirmed').mapped('balance'))
                r.total = abs(r.total_income - r.total_expense) + r.start_balance
                r.profited = r.total_income > r.total_expense
            else:
                r.total_income = 0
                r.total_expense = 0
                r.total = r.start_balance
                r.profited = True

    @api.model
    def create(self, vals):
        vals.update({'state': 'confirmed'})
        return super(Wallet, self).create(vals)
    
    # def write(self, vals):
    #     d = self.read()
    #     return super(Wallet, self).write({'first_name':vals.get('first_name', d[0]['first_name']), 'name':vals.get('first_name', d[0]['first_name']) + vals.get('last_name', d[0]['last_name'])})
            
    @api.depends('transaction_ids')
    def _compute_transaction_count(self):
        for r in self:
            if r.transaction_ids:
                r.transaction_count = len(r.transaction_ids)
                # r.transaction_count = self.env['transaction'].search_count([('wallet_id','=',r.id)])
            else:
                r.transaction_count = 0
    
    def action_open_transaction_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('manager_money.transaction_action')
        action['domain'] = "[('wallet_id','=',{})]".format(self.id)
        return action
    
    @api.model
    def _update_name_wallet(self):
        all_wallet = self.search([])
        for wallet in all_wallet:
            wallet.name = wallet.name.lstrip(' ')
            # print(wallet.name)
    
    # Test method ORM
                 
    # override method name_get  
    # @api.model
    def name_get(self):
        result = []
        # print(self)
        for wallet in self:
            str = 'Wallet: ' + wallet.name
            result.append((wallet.id, str))
       
        # print(result) # return [(1, 'Wallet: Chi tiêu cá nhân')]
        return result

    # default_get 
    def method_default_get(self):
        print(type(self))
        print(type(self.env['wallet']))
        print(type(super()))
        r = super(Wallet, self).default_get(['profited', 'state', 'total_income', 'transaction_count', 'transaction_ids', 'test'])
        # r = self.default_get(['profited', 'state', 'total_income'])
        # r = self.env['wallet'].default_get(['profited', 'state', 'total_income'])
        print(r)  # return {'profited': True, 'state': 'draft', 'total_income': 0.0}

    # override method name_create
    # @api.model
    def name_create(self, name):
        # record1 = self.env['wallet'].name_create('Test Create Name 1')
        # record2 = self.name_create('Test Create Name 2')
        # record3 = super(Wallet,self).name_create('Test Create Name 3')
        # print(record1) # return (12, 'Wallet: Test Create Name 1')
        # print(record2) # return (13, 'Wallet: Test Create Name 2')
        # print(record3) # return (14, 'Wallet: Test Create Name 3')
       
        return self.create({'name': name + 'override'}).name_get()[0]
    
    # method_search
    def method_search(self):
        w = super(Wallet, self).search([])
        # print(w)
        # r = self.env['transaction'].search([('status', '=', 'confirmed'), ('type', '=', 'income')], limit=5, order='date', count=False)
        # r2 = self.env['transaction'].search([('status', '=', 'confirmed'), ('type', '=', 'income')], limit=5, order='date', count=True)
        # print(r.name_get()[0])  # return transaction(1, 5, 8, 10)
        # print(r2)  # return 4
        # vals = [{
        #     'note':'Dung 3 '
        #     },{'note':'Dung 4'}]
        # self.env['transaction'].create(vals )
        group_guest = self.env.ref('manager_money.group_guest')
        ids = group_guest.read()[0]['users']
        list_users = self.env['res.users'].browse(ids).exists()
  
        # for u in list_users:
        #     if u.login == 'guest':
        #         t = self.with_user(u)
        #         print(w.env)
        #         w_new = w.with_env(self.env)
        #
        #         print(w_new.env)
        #         for i in w_new:
        #              print(i.env)
               
                # print(t.env.user.login)
                # print(t.read())
        
    # method_search_count
    def method_search_count(self):
        count = self.env['transaction'].search([], limit=1)
        
        print(count)  # return 13
        print(type(count))
        count2 = self.env['transaction'].search_count([('type', '=', 'income')])
        print(count2)  # return 7
    
    # method_name_search name search trả về cùng kiểu với name get
    @api.model
    def name_search(self, name, args, operator='ilike', limit=5):
         # wallet = self.name_search('Test Create', [('id', '=', '12')], 'like', limit = 5)
        # wallet = self.env['wallet'].name_search('Test Create', [('id', '=', '12')], 'like', limit = 5)
        # return [(12, 'Wallet: Test Create Name 1')]
        return super(Wallet, self.with_context(active_test=False)).name_search(name, [], operator, limit=limit)

    # method _read
    def method_read(self):
       # print(self.env.context)
       # context = self.env.context.copy()
       # print(context)
       print(self._context)
       print(type(self._context))
       # self_new = self.with_context({'test':'te'})
       # self_new = self.with_context({},test='te')
       self_new = self.with_context(test='te')
       print(self_new._context)
        # wallets = self.search([('active', '=', False)])
        # wallets.write({'active':True})
        # print(self.read())  # return list dict model
        # print(self.ids)
        # print(self.env['wallet'])
        # print(self.env.user)
        # print(self.ensure_one())
        # print(self.exists())
        # print(self.name_get())
        # print(self.get_metadata())
        # print(self.env.context)
        # print(self._context)
        # t = self.env['transaction'].search_read([('type', '=', 'income'), ['id']])
        # print(t)
        # t = self.env['transaction'].search([('id','=',71)])
        # print(t.read())
        # print(self.env)
        # t = super(Wallet, self).env['transaction'].browse([1000, 1001, 1])
        # print(super(Wallet, self).env)
        # print(self.env['transaction'].env.lang)
        # print(self.env['transaction'].env.user)
        # print(self.env['transaction'].env.company)
        # print(self.env['transaction'].env.cr)
        # print(self.env['transaction'].sudo().env.su)
        # print(self.env['transaction'].env.companies)
        # for i in t:
        #     if i.exists():
        #         print(i.get_metadata())
        
        # w = self.env['wallet'].with_context(active_test=False).search([])
        # print(self.env['wallet'].search([]))
        # print(w)
        # print(t.exists())

    # method read_group
    def method_read_group(self):
        trans = self.env['transaction'].read_group([], ['balance', 'date', 'type', 'status', 'note', 'id'], ['date'], lazy=False)
        print(trans)
        # print(trans[0]['__context'])

    # return lazy False
    # [
    # {
    #     '__count': 2,
    #      'type': 'expense',
    #      'status': 'canceled',
    #      '__domain': 
    #         [
    #            '&',
    #             ('type', '=', 'expense'),
    #             ('status', '=', 'canceled')
    #         ]
    # }
    # ]
    # return lazy True
    # [
    #     {
    #         'type_count': 8,
    #         'type': 'expense',
    #         '__domain': [('type', '=', 'expense')],
    #         '__context': {'group_by': ['status']}
    #       }
    #     ]

    # fields_get
    def method_fields_get(self):
        # t = self.env['transaction'].fields_get()
        # print(t)  # return error
        r = self.env['transaction'].fields_get(['status'], [])
        print(r)  # return {'start_balance': {'store': True, 'string': 'Start Balance'}, 'total': {'store': False, 'string': 'Total'}, 'transaction_ids': {'store': True, 'string': 'List Transactions'}}
        
    # fields_view_get
    def method_fields_view_get(self):
        print(self.env.ref('manager_money.transaction_view_tree').read())
        transaction_view_tree = self.env.ref('manager_money.transaction_view_tree').id
        view_id = self.env['transaction'].fields_view_get(view_id=transaction_view_tree)
        print(view_id)
        view_type = self.env['transaction'].fields_view_get(view_type='form')
        print(view_type)
    
    def unlink(self):
        for r in self:
            print(r.name)
        # print(super().env)
        # print('dhsfjdf')
        # print(super(Transaction,self))
        # print(super())
        return super(Wallet, self).unlink()
        # super().unlink()
    
    def method_filtered(self):
        trans = self.env['transaction'].search([])
        print(trans)  # return transaction(2, 4, 6, 7, 22, 24)
        # t = trans.filtered(lambda t: t.status == 'confirmed')
        # print(t)  # return transaction(2, 6)
        print(trans.env.cache)
        t2 = trans.filtered('wallet_id.name')
        
        
        print(t2)  # lọc những record có wallet_id return transaction(2, 4, 7, 22, 24)
        print(t2.env.cache)
        t3 = trans.filtered('note')
        t2.env.cache._data
        print(t3)
        print(t2.env.cache._data)
        print(t2 + t3)
        # t4 = trans.filtered('wallet_id')
        # print(t4)
        
    def method_filtered_domain(self):
        trans = self.env['transaction'].search([])
        print(trans)  # return transaction(1, 2, 3, 4, 5, 6, 7, 8, 10, 21, 22, 24) 
        t = trans.filtered_domain([('status', '=', 'draft')])
        print(t)  # return transaction(21, 22, 24)
        t2 = trans.filtered_domain([('wallet_id', '!=', None)])
        print(t2)  # return transaction(1, 2, 3, 4, 5, 6, 7, 8, 10, 21, 22, 24)
    
    # def _mapped_test(self):
    #     return 'note'
    
    def method_mapped(self):
        # a = self.search([])
        # a2 = super().search([])
        # a3 = super(Wallet,self).search([])
        # a4 = self.env['wallet'].search([])
        # print(a)
        # print(a2)
        # print(a3)
        # print(a4)
        # print(type(self))
        a = self.env['transaction'].search([])
        print(a.read())
        t = a.mapped('wallet_id')
        print(a)
        print(a.mapped('wallet_id.name'))
        print(a.mapped(lambda r: r.wallet_id))
        print(a.mapped(lambda r: (r.wallet_id, r.wallet_id.transaction_ids)))
        print(a.mapped(lambda r: (r.id)))
        print(t)
        print(a.mapped('wallet_id.transaction_ids'))
        print(a.mapped('wallet_id.transaction_ids.category_id'))
        w1 = self.env['wallet'].search([])
        t2 = w1.mapped('transaction_ids')
        print(t2)
      
        # b = a.mapped('transaction_oneday_id')
       
        # print(a.browse([100]).read())
        # b = a.transaction_oneday_id
        # d = a.mapped('type')
        # c = a.mapped('transaction_oneday_id.transaction_ids.wallet_id.transaction_ids.currency_id')
        # print(b)
        # print(c)
        # print(d)
        
    def method_sorted(self):
        transactions = self.env['transaction'].search([], limit=10)
        # print(transactions.sorted('id',True))
        print(transactions)
        # s = transactions.sorted(lambda t: t. or t.balance)
        # s2 = transactions.sorted(lambda t: t.note)
        # print(s.read(['wallet_id','balance']))
        # print(s2)
        # print(s.mapped('note'))

    # (0,0,values)
    # Thêm 1 record được tạo mới với values
    def write_zero(self):
        w = self.search([('name', '=', 'ef')])
        w.write({'transaction_ids':[(0, 0, {'note':'test', 'category_id':1, 'date':fields.Datetime.now()})]})
        print(w.transaction_ids)

    # (1,id,values)
    # update bản ghi có id là id với values
    def write_one(self):
        w = self.search([('name', '=', 'ef')])
        w.write({'transaction_ids':[(1, 69, {'note':'Test 3'})]})
        print(w.transaction_ids)

    # (2,id,0)
    # xoá bản ghi trong recordset có id là id , sau đó xoá luôn bản ghi đó trong db
    def write_two(self):
        w = self.search([('name', '=', 'ef')])
        print(w.transaction_ids)
        w.write({'transaction_ids':[(2, 39, 0)]})
        print(w.transaction_ids)

    # (3,id,0)
    # Xoá bản ghi trong recordset có id là id nhưng k xoá nó trong db
    def write_three(self):
        w = self.search([('name', '=', 'ef')])
        print(w.transaction_ids)
        w.write({'transaction_ids':[(3, 44, 0)]})
        print(w.transaction_ids)

    # (4,id,0)
    # Thêm bản ghi có sẵn có id là id vào recordset hiện tại
    def write_four(self):
        t = self.env['wallet'].search([('id', '=', self.id)])
        print(t.read()[0]['transaction_ids'])
        # t.write({'transaction_ids':[(6,0,[15,16])]})
        #
        # print(t.read()[0]['transaction_ids'])
        t.create({'name':'test 2', 'transaction_ids':[(4, 18, 0)]})
        # w = self.search([('name', '=', 'ef')])
        # print(w.transaction_ids)
        # w.write({'transaction_ids':[(4, 38, 0)]})
        # print(w.transaction_ids)

    # (5,0,0)
    # Xoá tất cả bản ghi trong recordset hiện tại, tương đương việc dùng lệnh 3 với mỗi record
    def write_five(self):
        w = self.search([('name', '=', 'ef')])
        w.write({'transaction_ids':[(5, 0, 0)]})
        print(w.transaction_ids)

    # (6,0,[ids])
    # Thay thế tất cả record hiện tại trong recordset bằng list record mới có id trong ids
    def write_six(self):
        w = self.search([('name', '=', 'ef')])
        w.write({'transaction_ids':[(6, 0, [44, 45])]})
        print(w.transaction_ids)
        
    def check_date(self):
        t = self.env['transaction'].search([], limit=1)
        # print(t.date)
        # d = fields.Datetime.add(t.date, t.date)
        # print(d)
        # print(fields.Datetime.today())
        # print(fields.Datetime.context_timestamp(t, datetime.today()))
        # all_wallet = self.search([])
        # for wallet in all_wallet:
        #     wallet.name = wallet.name.lstrip('AAADDD ')
        #     print(wallet.name)
        # group_guest = self.env.ref('manager_money.group_guest')
        # r = self.env['category'].with_user(group_guest).search([])
        # print(r)
       
    def action_read_wallet(self):
        print(self.env['res.users'].search([('id', '=', self.env.ref('manager_money.group_user').read()[0]['users'][0])]).get_metadata())
        s1 = self.env['transaction'].search([], limit=2)
        s2 = self.env['transaction'].search([], offset=1, limit=3)
        s3 = self.env['transaction'].search([], offset=1, limit=3)
        s4 = self.env['transaction'].search([], offset=2, limit=3)
        print(s1)
        print(s2)
        print(s3)
        print(s4)
        print(s1 + s2)
        print(s1 & s2)
        print(s1 - s2)
        print(s1 > s2)
        print(s2 >= s3)
        print(s3 >= s4)
        print(s3 <= s4)
        print(s1 | s2)
        # self.ensure_one()
        # return {
        #     # 'name': self.name,
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'list',
        #     'view_mode': 'tree,form',
        #     'res_model': 'transaction.oneday',
        #     # 'res_id': self.id,
        # } 

    def check_query(self):
        # self.env['transaction'].flush(self.env['transaction']._fields)
        # t = self._cr.execute("SELECT * FROM transaction t WHERE t.wallet_id = %s ", [self.id])
        # print(self.env.cr.dictfetchall())
        r1 = self.env['transaction'].search([],limit=1)
        r2=self.env['transaction'].search([],limit=2)
        print(r1)
        print(r2)
        return {
            "type": "ir.actions.act_url",
            "url": "http://localhost:8069/manager_money/wallets/1",
            "target": "new",
        }
