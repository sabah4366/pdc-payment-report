from odoo import models, fields, api, _
from datetime import datetime


class CustomerReportWizard(models.TransientModel):
    _name = 'customer.account.report.wizard'

    def get_todat(self):
        to_day = datetime.today()
        return to_day

    to_date = fields.Date(string= "Date", default=get_todat)
    partner_id = fields.Many2one('res.partner', string="Customer")

    def print_report(self):
        data = {
            'end_date': self.to_date,
            'partner_id': self.partner_id.id
        }
        return self.env.ref(
            'account_statement_report.action_report_print_statement').report_action(
            self, data=data)

    def print_report_xls(self):
        data = {
            'company': self.env.company.id,
        }
        return self.env.ref(
            'account_statement_report.hanifa_account_statement_xls').report_action(
            self, data=data)