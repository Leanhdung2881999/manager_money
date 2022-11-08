from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Category(models.Model):
    _name = 'category'
    _description = 'Category Transaction'
    _parent_name = 'parent_category_id'
    _parent_store = False
    _rec_name = 'name'
    
    name = fields.Char(string='Name Category', required=True, translate=True)
    icon = fields.Char(string='URL Icon', required=True)
    # embed_code = fields.Html(string="Icon", readonly=True, sanitize=True, sanitize_tags=True,
    #     sanitize_attributes=True, sanitize_style=False, strip_classes=False, strip_style=False)
    
    embed_code = fields.Html(string="Icon", compute="_compute_embed_code", store=True, sanitize=True, sanitize_tags=True, 
        sanitize_attributes=True, sanitize_style=False, strip_classes=False, strip_style=False)
    
    test= fields.Text(string="Test")
    test2 = fields.Html(string='Test2',sanitize=False, sanitize_tags=False,  sanitize_style=True)
    
    parent_category_id = fields.Many2one(comodel_name='category', string="Parent ID", index=True, ondelete="cascade", groups="manager_money.group_admin")
    parent_path = fields.Char(string="Parent Path",index=True,compute='_compute_parent_path',store=True, readonly=True)
    transaction_ids = fields.One2many('transaction', 'category_id', string='Type Category of Transactions')
    
    @api.constrains('parent_category_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursivecategories.')
    
    # @api.onchange('parent_category_id','name')
    # def _onchange_parent_path(self):
    #     if self.name:
    #         self.parent_path = '/'.join([self.parent_category_id.parent_path if self.parent_category_id.parent_path else '',self.name]).lstrip('/')
    
    @api.depends('parent_category_id', 'name')
    def _compute_parent_path(self):
        print('test')
        for r in self:
            if r.name:
                r.parent_path = '/'.join([r.parent_category_id.parent_path if r.parent_category_id.parent_path else '', r.name]).lstrip('/')
    
    @api.depends('icon')
    def _compute_embed_code(self):
        for image in self:
            if not image.icon:
                continue
            else:
                image.embed_code = '<img src="{}" alt="" width="20" height="20">'.format(image.icon)
    
    # @api.onchange('icon')
    # def _onchange_embed_code(self):
    #     self.ensure_one()
    #     if self.icon:
    #         self.embed_code = '<img src="{}" alt="" width="20" height="20">'.format(self.icon)
        
