from odoo import http, exceptions, models, fields, api
from odoo.http import request
import email
import datetime


class Main(http.Controller):

    # @http.route('/manager_money/transactions', type='http', auth='none')
    @http.route('/manager_money/transactions', type='http', auth='public')
    # @http.route('/manager_money/transactions', type='http', auth='user')
    def transactions(self):
        print(request)
        transactions = request.env['transaction'].sudo().search([])
        # return transactions.read()
        # print(type(transactions.read()[0]['category_id']))
        # return transactions.read(['id','category_id','note','balance'])
        html_result = '<html><body><ul>'
        for transaction in transactions:
            html_result += "<li> %s </li>" % transaction.read(['id', 'category_id', 'note', 'balance'])[0]
        html_result += '</ul></body></html>'
        # return html_result
        return request.make_response(
            html_result, headers=[
                ('Last-modified', email.utils.formatdate((
                    fields.Datetime.to_datetime(
                    request.env['transaction'].sudo().search([], order='write_date desc', limit=1)
                    .write_date) - datetime.datetime(1970, 1, 1)).total_seconds(), usegmt=True))
                ])
        
    @http.route('/manager_money/category', type="http", auth="group_admin")
    def category(self):
        categories = request.env['category'].search([])
        html_result = '<html><body><ul>'
        for category in categories:
            html_result += "<li> %s </li>" % category.read(['id', 'name', 'embed_code', 'icon'])[0]
        html_result += '</ul></body></html>'
        return request.make_response(html_result, headers=[('Last-modified', email.utils.formatdate((
                    fields.Datetime.to_datetime(
                    request.env['category'].search([], order='write_date desc', limit=1)
                    .write_date) - datetime.datetime(1970, 1, 1)).total_seconds(), usegmt=True))])

    # @http.route('/manager_money/wallets', type='http', auth='user')
    @http.route("/manager_money/wallets/<model('wallet'):wallet>", type='http', auth='user')
    # def wallet_details(self, wallet_id):
    def wallet_details(self, wallet):
        # record = request.env['wallet'].browse(int(wallet_id)).exists()
        record = request.env['wallet'].browse(wallet.id).exists()
        if record:
            html_result = '<html><body>'
            html_result += '<h1>%s</h1>' % record.name
            html_result += '<h1>%s</h1>' % record.total
            html_result += '<h1>%s</h1>' % record.transaction_ids
            html_result += '</body></html>'
        else:
            html_result = '<html><body><h1>No have any wallet</h1></body></html>'
        return request.make_response(html_result, headers=[('wallet_id', wallet.id)])

    @http.route('/manager_money/demo_img', type='http', auth='none')
    def test_image(self):
        image_url = '/manager_money/static/src/img/play_game_map.png'
        html_result = """<html><body><img src="%s"/></body></html>""" % image_url
        return html_result
    
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'
    
    @classmethod
    def _auth_method_group_admin(self):
        self._auth_method_user()
        print(request.env.user)
        if not request.env.user.has_group('manager_money.group_admin'):
            raise exceptions.AccessDenied()
