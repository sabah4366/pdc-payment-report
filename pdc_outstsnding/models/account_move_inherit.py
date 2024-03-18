from odoo import api, fields, models,_
class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    pdc_invoices = fields.Many2many('invoice.pdc.line',string="Pdc Payment",compute='list_relatable_pdc')

    @api.depends('pdc_invoices')
    def list_relatable_pdc(self):
        for record in self:
            print('=======================================================', record.name)
            pdc_lines = self.env['invoice.pdc.line'].search([
                ('pdc_id.state', 'in', ['registered', 'deposited','done']),
                ('name', '=', record.name),
            ])

            record.pdc_invoices = [(6, 0, pdc_lines.ids)]
            for pdc in pdc_lines:
               print('--------------------', pdc.name)







