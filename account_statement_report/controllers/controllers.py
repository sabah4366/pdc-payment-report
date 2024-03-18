# -*- coding: utf-8 -*-
# from odoo import http


# class CustomerAccountStatementReport(http.Controller):
#     @http.route('/customer_account_statement_report/customer_account_statement_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_account_statement_report/customer_account_statement_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_account_statement_report.listing', {
#             'root': '/customer_account_statement_report/customer_account_statement_report',
#             'objects': http.request.env['customer_account_statement_report.customer_account_statement_report'].search([]),
#         })

#     @http.route('/customer_account_statement_report/customer_account_statement_report/objects/<model("customer_account_statement_report.customer_account_statement_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_account_statement_report.object', {
#             'object': obj
#         })
