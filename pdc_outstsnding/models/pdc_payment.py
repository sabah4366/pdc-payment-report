from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import timedelta,datetime,date

class PdcPayment(models.Model):
    _inherit = "pdc.wizard"

    has_invoices = fields.Boolean(string='Invoices')
    payment_boolean_first = fields.Boolean(default=False )
    payment_boolean_second = fields.Boolean(default=True )
    total_amount = fields.Float(string='Total Amount')
    partner_id = fields.Many2one('res.partner', string="Partner", tracking=True)
    invoice_pdc_id = fields.One2many('invoice.pdc.line','pdc_id',string="Invoice/Bill")
    rec_data = fields.Many2many(
        'account.move.line',
        string="Outstanding Amount",


    )
    jounal_line_ids = fields.One2many(
        'account.move.line','pdc_id',
        string="Outstanding Amount",


    )
    initial_amount = fields.Float(string="Total Recievable Amount",compute='get_payable_amount',store=True)
    pending_invoice_amount = fields.Monetary(string="Total Pending Amount" ,compute='get_total_amount' )
    view_total = fields.Boolean(string='show initial total')
    view_total_invoice = fields.Boolean(string='show invoice total',default = False)
    invoice_boolean = fields.Boolean(string=" Invoice/Bill?")
    # journal_boolean = fields.Boolean(string="Journal?")
    invoice_ids = fields.Many2many('account.move',store=True)
    payment_pdc = fields.Selection([('invoice_boolean', 'Invoice/Bill'), ('journal_boolean', 'Initial Balance')], 'PDC Payment',
                                   default="invoice_boolean")

    amount = fields.Monetary(string="Amount")




    # def has_invoices_checking(self):
    #     print('())))))))))))))))))))))))))))))))))))))))',self.has_invoices,self.invoice_ids,self.invoice_pdc_id)
    #     if self.invoice_ids:
    #         self.has_invoices = False
    #     elif self.invoice_pdc_id:
    #         self.has_invoices = True



    # def create(self,vals):
    #     event_id = super(PdcPayment, self).create(vals)
    #
    #     leads = self.env['account.move'].search(('id','in',self.account_move_ids))
    #     for lead in leads:
    #         lead.amount = [(4, [event_id.id])]
    #
    #
    #     lead.write({'meeting_ids': [(4, [event_id.id])]})
    @api.model
    def default_get(self, fields):
        print('*****************************************************')
        rec = super(PdcPayment, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec
        invoices = self.env['account.move'].browse(active_ids)

        memo = ''  # Initialize an empty string to store concatenated invoice names

        # Calculate the sum of 'amount_residual' for selected invoices
        total_amount_residual = sum(invoice.amount_residual for invoice in invoices)

        for invoice in invoices:
            if invoice.move_type in ('out_invoice', 'out_refund'):
                rec.update({'payment_type': 'receive_money'})
            elif invoice.move_type in ('in_invoice', 'in_refund'):
                rec.update({'payment_type': 'send_money'})

            # Concatenate the invoice names
            memo += invoice.name + '\n'

        rec.update({
            'partner_id': invoices[0].partner_id.id,
            'payment_amount': total_amount_residual,  # Update with the calculated sum
            'invoice_id': invoices[0].id,
            'due_date': invoices[0].invoice_date_due,
            'memo': memo,  # Set the concatenated memo,
        })

        return rec

    def button_register(self):
        self.change_payment()
        return super(PdcPayment, self).button_register()

    # def action_chnaging(self):
    #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1',self.invoice_pdc_id)
    #     listt = []
    #     if self:
    #         amount=0
    #         invoice_partial_amt=0
    #         amount_residual=0
    #         balance_amount = self.payment_amount
    #         first_line = True
    #         print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')
    #         for invoice_id in self.invoice_ids:
    #             print('blnc',balance_amount)
    #             print('amount first',invoice_id.amount, 'dueamtt', invoice_id.amount_residual,'due sec',invoice_id.amount_residual_value, 'part', invoice_id.invoice_partial_amt)
    #             if invoice_id.amount_residual_value > 0:
    #                 if balance_amount <= abs(invoice_id.amount_residual_value):
    #                     if first_line:
    #                         amount = abs(balance_amount)
    #                         invoice_partial_amt = abs(balance_amount + invoice_id.invoice_partial_amt)
    #                         amount_residual = abs(invoice_id.amount_residual_value - balance_amount)
    #                         first_line = False
    #                         print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
    #
    #                     else:
    #                         amount = 0
    #                         invoice_partial_amt = 0
    #                         amount_residual = invoice_id.amount_total
    #                         print('ttttttttttttttttttttttttttttttttt')
    #                 elif balance_amount > abs(invoice_id.amount_residual_value):
    #                     if first_line:
    #                         amount = abs(invoice_id.amount_residual_value)
    #                         invoice_partial_amt = abs(invoice_id.amount_total)
    #                         balance_amount = abs(balance_amount - abs(invoice_id.amount_residual_value))
    #                         amount_residual = abs(balance_amount - balance_amount)
    #
    #                         print('iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    #
    #                     elif not first_line:
    #                         amount = invoice_id.amount if invoice_id.amount else 0
    #                         invoice_partial_amt =  invoice_id.invoice_partial_amt if invoice_id.invoice_partial_amt else 0
    #                         amount_residual =  invoice_id.amount_residual_value if invoice_id.amount_residual_value else 0
    #                         print('ppppppppppppppppppppppppppppppppppppp')
    #             else:
    #                 if balance_amount <= abs(invoice_id.amount_residual):
    #                     if first_line:
    #                         amount = abs(balance_amount)
    #                         invoice_partial_amt = abs(balance_amount + invoice_id.invoice_partial_amt)
    #                         amount_residual = abs(invoice_id.amount_total - balance_amount)
    #                         first_line = False
    #                         print('---------------------------')
    #                     else:
    #                         amount = 0
    #                         invoice_partial_amt =  0
    #                         amount_residual = invoice_id.amount_total
    #                         print('=========')
    #                 elif balance_amount > abs(invoice_id.amount_residual):
    #                     if first_line:
    #                         amount = abs(invoice_id.amount_residual)
    #                         invoice_partial_amt = abs(invoice_id.amount_total)
    #                         balance_amount = abs(balance_amount - abs(invoice_id.amount_residual))
    #                         amount_residual = abs(balance_amount - balance_amount)
    #
    #                         print('+++++++++++')
    #
    #                     elif not first_line:
    #                         amount = 0
    #                         invoice_partial_amt = 0
    #                         amount_residual =  0
    #                         print('////////////')
    #             print('amount second', invoice_id.amount, 'dueamtt', invoice_id.amount_residual, 'due sec',
    #                   invoice_id.amount_residual_value, 'part', invoice_id.invoice_partial_amt)
    #             record = self.env['invoice.pdc.line'].create({
    #                 'pdc_invoice_id': invoice_id.id,
    #                 # 'amount': amount,
    #                 # 'amount_residual': amount_residual,
    #                 # 'invoice_partial_amt': invoice_partial_amt,
    #
    #             })
    #             # print('amount',amount,'dueamtt',amount_residual,'part',invoice_partial_amt)
    #             record.amount = amount
    #             record.amount_residual = amount_residual
    #             record.invoice_partial_amt = invoice_partial_amt
    #             self.invoice_pdc_id += record
    #
    #         if self.cheque_status == 'draft':
    #             self.write({'state': 'draft'})
    #
    #         if self.cheque_status == 'deposit':
    #             self.action_register()
    #             self.action_deposited()
    #             self.write({'state': 'deposited'})
    #
    #         if self.cheque_status == 'paid':
    #             self.action_register()
    #             self.action_deposited()
    #             self.action_done()
    #             self.write({'state': 'done'})
    #     # self.change_payment()

    def action_register_check(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        account_move_model = self.env[active_model].browse(active_id)

        if account_move_model.move_type not in ('out_invoice', 'in_invoice'):
            raise UserError("Only Customer invoice and vendor bills are considered!")

        move_listt = []
        payment_amount = 0.0
        payment_type = ''
        invoice_pdc_lines = []  # Accumulate invoice.pdc.line records here

        if len(active_ids) > 0:
            account_moves = self.env[active_model].browse(active_ids)
            partners = account_moves.mapped('partner_id')
            if len(set(partners)) != 1:
                raise UserError('Partners must be same')

            states = account_moves.mapped('state')
            if len(set(states)) != 1 or states[0] != 'posted':
                raise UserError('Only posted invoices/bills are considered for PDC payment!!')

            for account_move in account_moves:
                print('///////////////',account_move.name,account_move.amount_residual_value)
                if account_move.payment_state != 'paid' and account_move.amount_residual != 0.0:
                    payment_amount += account_move.amount_residual
                    record = self.env['invoice.pdc.line'].create({
                        'pdc_invoice_id': account_move.id,
                    })
                    invoice_pdc_lines.append((4, record.id))  # Append records to the list
                    move_listt.append(account_move.id)

        if not move_listt:
            raise UserError("Selected invoices/bills are already paid!!")

        if account_moves[0].move_type == 'in_invoice':
            payment_type = 'send_money'
        elif account_moves[0].move_type == 'out_invoice':
            payment_type = 'receive_money'

        return {
            'name': 'PDC Payment',
            'res_model': 'pdc.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sh_pdc.sh_pdc_wizard_form_wizard').id,
            'context': {
                'default_partner_id': account_move_model.partner_id.id,
                'default_payment_amount': payment_amount,
                'default_payment_type': payment_type,
                'default_invoice_pdc_id': invoice_pdc_lines,  # Assign the list of records
            },
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    @api.depends('rec_data','payment_amount')
    def get_payable_amount(self):
        # print('second function----------------------------------------------------------')
        tot_amount = 0
        total_value = 0
        for record in self:
            if record.rec_data:
                for rec in record.rec_data:
                    if rec.credit:
                        total_value += rec.credit
                    elif rec.debit:
                        total_value += rec.debit
                domain = [
                    ('partner_id', '=', record.partner_id.id),
                    ('state', 'in', ['registered', 'deposited']),

                ]
                records = self.env['pdc.wizard'].search(domain)

                if records:
                    for rec in records:
                        tot_amount += rec.amount
                    total_amount = total_value - tot_amount
                    record.initial_amount = total_amount
                else:
                    record.initial_amount = total_value

                if record.payment_amount > 0:
                    record.initial_amount = record.initial_amount - record.payment_amount
                else:
                    record.payment_amount = 0
            else:
                record.initial_amount=0
                # print('mikku')


    def action_register(self):
        pending_invoice_amount = round(self.pending_invoice_amount, 3)
        for rec in self.invoice_pdc_id:
            moves = self.env['account.move'].search([('name', '=', rec.name)])
            for move in moves:
                existing_data = self.env['invoice.pdc.line'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('name', '=', rec.name),], order='id desc', limit=1)
                for data in existing_data:
                    # print('sabah',data.amount,data.invoice_partial_amt,data.amount_residual)
                    move.write({
                        'amount': data.amount,
                        'invoice_partial_amt': data.invoice_partial_amt,
                        'amount_residual_value': data.amount_residual,
                    })

        if self.payment_pdc =='journal_boolean':
            if self.initial_amount == 0 or self.initial_amount < 0:
                raise UserError(_("No Receivable Amount Dues"))

        # elif self.payment_pdc=='invoice_boolean':
        #     if self.payment_type == 'receive_money':
        #         if self.payment_amount > pending_invoice_amount:
        #             raise UserError(_("Entered amount is more than payment amount"))
        #
        #         # elif pending_invoice_amount < self.payment_amount:
        #         #     raise UserError(_("Entered amount is less than payment amount"))
        #     else:
        #         if abs(pending_invoice_amount) > abs(self.payment_amount):
        #             print("self.pending_invoice_amount :",pending_invoice_amount)
        #             print("self.payment_amount :",self.payment_amount)
        #
        #             raise UserError(_("Entered amount is more than payment amount"))
        #         elif abs(pending_invoice_amount) < abs(self.payment_amount):
        #             raise UserError(_("Entered amount is less than payment amount"))

        return super(PdcPayment, self).action_register()



    # @api.depends('invoice_pdc_id.amount')
    # def onchange_payment_amount(self):
    #     print('bolllllln',self.payment_boolean_second)
    #     total=0
    #     if self.payment_boolean_first == False:
    #         for rec in self.invoice_pdc_id:
    #             total = total + rec.amount
    #
    #         self.payment_amount = total
    #         self.payment_boolean_second = False


            # if self.payment_amount == 0:
            #     return {'warning': {
            #         'title': _('Warning'),
            #         'message': _(
            #             'Please enter payment amount')
            #     }}




    @api.onchange('invoice_pdc_id')
    def existing_record_Value(self):

        for rec in self.invoice_pdc_id:
            model = self.env['account.move'].search([('name', '=', rec.name)])

            if not self.payment_amount and model.amount > 0:
                rec.amount_residual = model.amount_residual_value
                rec.amount = model.amount
                rec.invoice_partial_amt = model.invoice_partial_amt
                # print('insideee amount :',model.amount,'due', model.amount_residual_value,'partial',model.invoice_partial_amt)


    # @api.onchange('payment_amount')
    # def created_pdc_invoice(self):
    #     print('first function-----------------------------------------------------------')
    #     count = 0
    #     balance_amount = self.payment_amount
    #     existing_data = self.env['invoice.pdc.line'].search(
    #         [('partner_id', '=', self.partner_id.id), ('pdc_id.state', 'in', ['registered'])])
    #
    #     for rec in self.invoice_pdc_id:
    #         latest_record = existing_data.filtered(
    #             lambda r: r.pdc_invoice_id.name == rec.pdc_invoice_id.name).sorted(
    #             key=lambda r: r.create_date, reverse=True)[:1]
    #         if count < len(self.invoice_pdc_id):
    #             print('due after', rec.amount_residual, 'amount', rec.amount, 'partial', rec.invoice_partial_amt)
    #             if latest_record.amount:
    #                 rec.amount_residual = latest_record.amount_residual
    #                 rec.amount = latest_record.amount
    #                 rec.invoice_partial_amt = latest_record.invoice_partial_amt
    #                 print('rrrrrrrrrrrrrrrrrrrrrrr')
    #             print('blnc amt:',balance_amount,'amount_residual:',rec.amount_residual,'payment_amount:',self.payment_amount,'amount',rec.amount)
    #             if balance_amount <= rec.amount_residual and self.payment_amount and balance_amount != 0 :
    #                 print('latest amount_residual', latest_record.amount_residual,'rec amount_residual',rec.amount_residual )
    #                 if latest_record.total:
    #                     rec.amount = abs(balance_amount)
    #                     rec.invoice_partial_amt = abs(balance_amount + latest_record.invoice_partial_amt)
    #                     rec.amount_residual = abs(latest_record.amount_residual - balance_amount)
    #                     balance_amount = balance_amount - latest_record.amount_residual
    #                     if balance_amount < 0:
    #                         balance_amount = 0
    #                     print('balance amount 2nd', balance_amount)
    #
    #             elif balance_amount > rec.amount_residual and balance_amount != 0 and rec.amount > 0 and latest_record :
    #                 rec.amount = abs(rec.total)
    #                 rec.invoice_partial_amt = abs(rec.total)
    #                 rec.amount_residual = abs(balance_amount - balance_amount)
    #                 balance_amount = abs(balance_amount - latest_record.amount_residual)
    #                 print('balance amount 3rd', balance_amount, 'amount_residual', rec.amount_residual)
    #             else:
    #                 balance_amount = balance_amount - rec.total
    #                 print('tha tha tha')
    #             count += 1
    #         print('due', rec.amount_residual, 'amount', rec.amount, 'partial', rec.invoice_partial_amt)


    @api.onchange('payment_amount')
    def change_payment(self):
            self.get_total_amount()
            for rec in self:
                if rec.payment_pdc == "journal_boolean":
                    rec.amount = rec.payment_amount
                elif rec.payment_pdc == "invoice_boolean":
                    first_line = True
                    rec.amount = rec.payment_amount
                    balance_amount = rec.payment_amount
                    print('balance_amount', balance_amount)
                    for line in rec.invoice_pdc_id:
                        self.has_invoices = True
                        model = self.env['account.move'].search([('name', '=', line.name)])

                        print('balance amounttt first',balance_amount,'amount due',line.amount_residual,line.amount)
                        print('balance amounttt second',balance_amount,'amount due',model.amount_residual,model.amount)
                        if balance_amount <= abs(line.amount_residual) :
                            if first_line:
                                line.amount = abs(balance_amount)
                                # line.invoice_partial_amt = abs(balance_amount + model.invoice_partial_amt)
                                line.invoice_partial_amt = abs(model.invoice_partial_amt + balance_amount)  if model.invoice_partial_amt > 0 else abs(balance_amount + model.invoice_partial_amt)
                                line.amount_residual = abs(model.amount_residual_value - balance_amount)  if model.amount_residual_value > 0 else abs(abs(line.total )- balance_amount)
                                first_line = False
                                print('444444444444444')
                            else:
                                line.amount =  model.amount if model.amount else 0
                                line.invoice_partial_amt = model.invoice_partial_amt if model.invoice_partial_amt else 0
                                line.amount_residual = model.amount_residual if model.amount_residual else line.total
                                print('333333333333333')
                        elif balance_amount > abs(line.amount_residual) :
                            if first_line:
                                line.amount = abs(line.amount_residual)
                                line.invoice_partial_amt = abs(line.total)
                                balance_amount = abs(balance_amount - abs(line.amount_residual))
                                line.amount_residual = abs(balance_amount - balance_amount)

                                print('2222222222222222')

                            elif not first_line:
                                line.amount = model.amount if model.amount else 0
                                line.invoice_partial_amt =  model.invoice_partial_amt if model.invoice_partial_amt else 0
                                line.amount_residual = model.amount_residual if model.amount_residual else 0
                                print('111111111111111111')
                        print('amount', line.amount, 'due amount', line.amount_residual, 'partial',line.invoice_partial_amt)



    @api.depends('payment_amount','invoice_pdc_id')
    def get_total_amount(self):
        if self.invoice_ids:
            self.has_invoices = True
        elif self.invoice_pdc_id:
            self.has_invoices = False
        print('////////////////////////////////////////////////////////////////////////////////////',self.has_invoices)
        for rec in self:
            rec.pending_invoice_amount = rec.payment_amount
            for line in rec.invoice_pdc_id:
                if not line.amount:
                    line.amount_residual = line.total
                if line.amount:
                    # line.amount_residual = abs(line.total)-abs(line.amount)
                    # total_amount +=line.amount
                    rec.pending_invoice_amount = line.amount_residual

    def action_done(self):
        move = self.env['account.move']
        # print(move,'move')

        self.check_payment_amount()  # amount must be positive
        pdc_account = self.check_pdc_account()
        bank_account = self.journal_id.payment_debit_account_id.id or self.journal_id.payment_credit_account_id.id
        # bank_account = self.env.company.account_journal_payment_debit_account_id.id or self.env.company.account_journal_payment_credit_account_id.id

        # Create Journal Item
        move_line_vals_debit = {}
        move_line_vals_credit = {}
        if self.payment_type == 'receive_money':
            move_line_vals_debit = self.get_debit_move_line(bank_account)
            move_line_vals_credit = self.get_credit_move_line(pdc_account)
        else:
            move_line_vals_debit = self.get_debit_move_line(pdc_account)
            move_line_vals_credit = self.get_credit_move_line(bank_account)

        if self.memo:

            move_line_vals_debit.update({'name': 'PDC Payment :' + self.memo, 'partner_id': self.partner_id.id})
            move_line_vals_credit.update({'name': 'PDC Payment :' + self.memo, 'partner_id': self.partner_id.id})

        else:
            move_line_vals_debit.update({'name': 'PDC Payment', 'partner_id': self.partner_id.id})
            move_line_vals_credit.update({'name': 'PDC Payment', 'partner_id': self.partner_id.id})

        # create move and post it
        move_vals = self.get_move_vals(
            move_line_vals_debit, move_line_vals_credit)
        move_vals['payment_state'] = 'not_paid'

        # invoice = self.env['account.move'].sudo().search([('name','=',self.memo)])
        # if invoice:
        total_amount_residuals = sum(self.invoice_ids.mapped('amount_residual'))
        # print(total_amount_residuals,'total_amount_residuals')
        if self.invoice_ids and total_amount_residuals != 0:
            # print(move_vals)
            move_id = move.create(move_vals)
            # print("New Move", move_id)
            # print("Move Values",move_vals)
            move_id.write({'payment_state': 'not_paid'})
            move_id.action_post()
            # print(move_id.payment_state,'move_id')
            # payment_amount = self.payment_amount
            for invoice in self.invoice_ids:
                amount = invoice.amount
                residual = invoice.amount_residual_signed
                if self.payment_type == 'receive_money':
                    # reconcilation Entry for Invoice
                    debit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', invoice.id),
                                                                                 ('debit', '>', 0.0)], limit=1)

                    credit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', move_id.id),
                                                                              ('credit', '>', 0.0)], limit=1)

                    if debit_move_id and credit_move_id and amount > 0:
                        full_reconcile_id = self.env['account.full.reconcile'].sudo().create({})

                        # if payment_amount > invoice.amount_residual:
                        #     amount = invoice.amount_residual
                        #
                        # else:
                        #     amount = payment_amount
                        # payment_amount -= invoice.amount_residual
                        abc = {'debit_move_id': debit_move_id.id,
                               'credit_move_id': credit_move_id.id,
                               'amount': amount,
                               'debit_amount_currency': amount,
                               'credit_amount_currency': 0
                               }
                        partial_reconcile_id_1 = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': debit_move_id.id,
                             'credit_move_id': credit_move_id.id,
                             'amount': amount,
                             'debit_amount_currency': amount,
                             'credit_amount_currency': amount
                             })

                        # partial_reconcile_id_2 = self.env['account.partial.reconcile'].sudo().create({'debit_move_id': self.deposited_debit.id,
                        #                                                     'credit_move_id':self.deposited_credit.id,
                        #                                                     'amount':amount,
                        #                                                     'debit_amount_currency':amount,
                        #
                        #                                                 })

                        if invoice.amount_residual == 0:
                            involved_lines = []

                            debit_invoice_line_id = self.env['account.move.line'].search(
                                [('move_id', '=', invoice.id), ('debit', '>', 0)], limit=1)
                            partial_reconcile_ids = self.env['account.partial.reconcile'].sudo().search(
                                [('debit_move_id', '=', debit_invoice_line_id.id)])

                            for partial_reconcile_id in partial_reconcile_ids:
                                involved_lines.append(partial_reconcile_id.credit_move_id.id)
                                involved_lines.append(partial_reconcile_id.debit_move_id.id)
                            self.env['account.full.reconcile'].create({
                                'partial_reconcile_ids': [(6, 0, partial_reconcile_ids.ids)],
                                'reconciled_line_ids': [(6, 0, involved_lines)],
                            })

                        involved_lines = [self.deposited_debit.id, self.deposited_credit.id]

                        self.env['account.full.reconcile'].create({
                            'partial_reconcile_ids': [(6, 0, [partial_reconcile_id_1.id])],
                            'reconciled_line_ids': [(6, 0, involved_lines)],
                        })

                else:
                    # reconcilation Entry for Invoice
                    credit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', invoice.id),
                                                                                  ('credit', '>', 0.0)], limit=1)

                    debit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', move_id.id),
                                                                                 ('debit', '>', 0.0)], limit=1)

                    if debit_move_id and credit_move_id and amount > 0:

                        # if payment_amount > invoice.amount_residual:
                        #     amount = invoice.amount_residual
                        #
                        # else:
                        #     amount = payment_amount

                        # payment_amount -= invoice.amount_residual

                        partial_reconcile_id_1 = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': debit_move_id.id,
                             'credit_move_id': credit_move_id.id,
                             'amount': amount,
                             'credit_amount_currency': amount
                             })
                        partial_reconcile_id_2 = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': self.deposited_debit.id,
                             'credit_move_id': self.deposited_credit.id,
                             'amount': amount,
                             'debit_amount_currency': amount,
                             'credit_amount_currency': amount})

                        if invoice.amount_residual == 0:
                            involved_lines = []

                            credit_invoice_line_id = self.env['account.move.line'].search(
                                [('move_id', '=', invoice.id), ('credit', '>', 0)], limit=1)
                            partial_reconcile_ids = self.env['account.partial.reconcile'].sudo().search(
                                [('credit_move_id', '=', credit_invoice_line_id.id)])

                            for partial_reconcile_id in partial_reconcile_ids:
                                involved_lines.append(partial_reconcile_id.credit_move_id.id)
                                involved_lines.append(partial_reconcile_id.debit_move_id.id)
                            self.env['account.full.reconcile'].create({
                                'partial_reconcile_ids': [(6, 0, partial_reconcile_ids.ids)],
                                'reconciled_line_ids': [(6, 0, involved_lines)],
                            })

                        involved_lines = [self.deposited_debit.id, self.deposited_credit.id]

                        self.env['account.full.reconcile'].create({
                            'partial_reconcile_ids': [(6, 0, [partial_reconcile_id_1.id])],
                            'reconciled_line_ids': [(6, 0, involved_lines)],
                        })
                # if amount > 0 and residual != 0:
                #     invoice._compute_payment_state()
        else:
            bank_account = self.journal_id.payment_debit_account_id.id or self.journal_id.payment_credit_account_id.id
            # bank_account = self.env.company.account_journal_payment_debit_account_id.id or self.env.company.account_journal_payment_credit_account_id.id

            partner_account = self.get_partner_account()
            debit_move_line = {
                'pdc_id': self.id,
                'partner_id': self.partner_id.id,
                'account_id': bank_account if self.payment_type == 'receive_money' else partner_account,
                'debit': self.payment_amount,
                'ref': self.memo,
                'date': self.due_date,
                'date_maturity': self.due_date,
            }

            credit_move_line = {
                'pdc_id': self.id,
                'partner_id': self.partner_id.id,
                'account_id': partner_account if self.payment_type == 'receive_money' else bank_account,
                'credit': self.payment_amount,
                'ref': self.memo,
                'date': self.due_date,
                'date_maturity': self.due_date,
            }

            move_vals = {
                'pdc_id': self.id,
                'date': self.due_date,
                'journal_id': self.journal_id.id,
                'ref': self.memo,
                'line_ids': [(0, 0, debit_move_line),
                             (0, 0, credit_move_line)]
            }

            move = self.env['account.move'].create(move_vals)
            move.action_post()

        self.write({
            'state': 'done',
            'done_date': date.today(),
        })
        # for invoice in self.invoice_ids:
            # if invoice.amount > 0:
            #     invoice._compute_amount()





    def action_returned(self):
        res = super(PdcPayment, self).action_returned()
        for line in self.invoice_ids:
            line.amount_residual_signed = line.amount_residual_signed + line.amount
            line.amount = 0
        return res

    def action_bounced(self):
        res = super(PdcPayment, self).action_bounced()
        for line in self.invoice_ids:
            line.amount_residual_signed = line.amount_residual_signed + line.amount
            line.amount = 0
        return res

    def action_cancel(self):
        res = super(PdcPayment, self).action_cancel()
        for line in self.invoice_ids:
            line.amount_residual_signed = line.amount_residual_signed + line.amount
            line.amount = 0
        return res

    # @api.onchange('invoice_pdc_id')
    # def _get_amt_pdc(self):
    #     print('hhhh')
    #     for rec in self.invoice_pdc_id.pdc_invoice_id:
    #         print('pppppppppppppppppppppppppppppp')
    #         if rec.amount == 0:
    #             rec.amount_residual_signed = rec.amount_residual
    #         if rec.amount > 0:
    #             print('kkkkkkkkk')
    #             rec.amount_residual_signed = rec.amount_residual_signed - rec.invoice_partial_amt

    #     res = super(PdcPayment, self)._onchange_invoice_ids()
    #     self.payment_amount=self.payment_amount
    #     return res
        # total_amount = 0
        # for rec in self:
        #
        #     rec.pending_invoice_amount = rec.payment_amount
        #     print(rec.pending_invoice_amount)
        #     print(rec.payment_amount, 'rec.payment_amount')
        #     for line in rec.invoice_ids:
        #         total_amount += line.amount
        #         rec.pending_invoice_amount = total_amount
        #         print(rec.pending_invoice_amount)

    #
    # @api.onchange('payment_amount')
    # def onchange_invoice_ids(self):
    #     total_sum = 0.00
    #     for record in self:
    #         if record.invoice_ids:
    #             for rec in record.invoice_ids:
    #                 print(rec, 'rec')
    #                 if rec.amount_residual - rec.total_pdc_payment > 0:
    #                     total_sum += rec.amount_residual - rec.total_pdc_payment
    #                     record.pending_invoice_amount = total_sum
    #         else:
    #             record.pending_invoice_amount = 0

    # @api.onchange('partner_id')
    # def onchange_partner(self):
    #     if self.partner_id:
    #         if self.payment_pdc == "journal_boolean":
    #             print("===========================================")
    #             domain = [
    #                 ('partner_id', '=', self.partner_id.id),
    #                 ('move_id.move_type', '=', 'entry'),
    #                 ('account_id.user_type_id.type', '=', 'receivable'),
    #                 ('move_id.journal_id.type', 'in', ['general', 'sale']),
    #             ]
    #             self.rec_data = self.env['account.move.line'].search(domain)
    #
    #             # done by namitha and muhsina
    #         elif self.payment_pdc == 'invoice_boolean':
    #             pass
    #             # print("-----------------------------------------")
    #             # domain = [
    #             #     ('partner_id', '=', self.partner_id.id),
    #             #     ('move_type', '=', 'out_invoice'),
    #             #     ('payment_state', 'in', ['not_paid','partial']),
    #             #     ('state', 'in', ['posted']),
    #             # ]
    #             # pdc_data = self.env['account.move'].search(domain)
    #             # self.invoice_pdc_id.pdc_invoice_id = pdc_data
    #



        # else:
        #     self.rec_data = False
        #     # done by namitha and muhsina
        #     # self.invoice_pdc_id.pdc_invoice_id = Falseis_registered


class PdcPaymentLine(models.Model):
    _name = "invoice.pdc.line"


    flag_boolean = fields.Boolean()
    pdc_id = fields.Many2one('pdc.wizard',string='PDC ID')
    partner_id = fields.Many2one('res.partner',related='pdc_id.partner_id', string='Partner')
    pdc_invoice_id = fields.Many2one('account.move', string='Number')




    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 store=True, readonly=True,
                                 )
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                          related='company_id.currency_id')
    due_date = fields.Date(string='Due Date',related='pdc_invoice_id.invoice_date_due')

    amount_untax = fields.Monetary(string='Tax Excluded',related='pdc_invoice_id.amount_untaxed_signed',currency_field='company_currency_id')
    name = fields.Char(string='Name',related='pdc_invoice_id.name')
    total = fields.Monetary(string='Total',related='pdc_invoice_id.amount_total_signed',currency_field='company_currency_id')
    amount_residual = fields.Monetary(string='Amount Due',currency_field='company_currency_id')
    amount = fields.Float(string='Amount',currency_field='company_currency_id', store=True)

    @api.onchange('amount')
    def onchange_amount(self):
        payment_amount=0


        for rec in self:
            moves = self.env['account.move'].search([('name', '=', rec.name)])
            # print('moves record',moves.name,moves.amount,moves.invoice_partial_amt,moves.amount_residual_value)
            if moves.amount:
                balance = rec.amount
                rec.amount = rec.amount
                rec.invoice_partial_amt = moves.invoice_partial_amt + balance
                rec.amount_residual = moves.amount_residual_value - balance
                # print('haiiiii')
            else:

                balance = rec.amount
                rec.amount = rec.amount
                rec.invoice_partial_amt =  balance
                rec.amount_residual = abs(rec.total) - balance
                # print('inside of after  ', rec.amount,rec.invoice_partial_amt,rec.amount_residual)
                # print('helloo')








    invoice_partial_amt = fields.Float(string='Partial Amt',currency_field='company_currency_id',store=True)
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status", store=True, readonly=True, copy=False, tracking=True,
        related='pdc_invoice_id.payment_state')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        related='pdc_invoice_id.state')




class PdcInvoice(models.Model):
    _inherit = "account.move"

    amount = fields.Float(string='Amount', help='The amount of the account move')
    invoice_partial_amt = fields.Float(string='Partial Amt')
    is_registered = fields.Boolean(default=False)
    amount_residual_value = fields.Float(string='Amount Due')








class PdcInvoiceline(models.Model):
    _inherit = "account.move.line"

    amount_line = fields.Float(string='Amount', help='The amount of the account move')
    pdc_id = fields.Many2one('pdc.wizard','jounal_line_ids')
    initial = fields.Boolean(string="Initial",default = False)