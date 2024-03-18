from odoo import models, fields, api


class CollectionSaleReportPdf(models.AbstractModel):
    _name = 'report.account_statement_report.report_statement'

    def _get_report_values(self, docids, data=None):

        partner_id = self.env['res.partner'].browse(data['partner_id'])
        company_id = self.env.company

        partner_details = {
            'name': partner_id.name,
            'street': partner_id.street,
            'street2': partner_id.street2,
            'city': partner_id.city,
            'state': partner_id.state_id.name,
            'country': partner_id.country_id.name,
            'zip': partner_id.zip,
            'contact1': partner_id.phone,
            'contact2': partner_id.mobile,
        }

        statements_of_customer_template = {
            'get_pdc_details': self._get_pdc_details(data),
            'get_statement_details': self._get_statement_details(data),

            'vendor_bills': self._get_vendor_bill_details(data),
            'check_journal_entries': self._get_journal_entries_details(data),
            'data': data,
            'partner_details': partner_details,
            'company': company_id,
            'grand_total': self._get_total(data),
            'entry_total': self._get_entry_total(data),
            'check_status': self._get_status(data),
            'check_entries_ret': self._get_entries_ret(data),
            # 'get_cash_details': self._get_cash_details(data),

        }
        return statements_of_customer_template

    def _get_pdc_details(self, data):
        rec_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id),
             ('partner_id', '=', data['partner_id']),
             ('move_type', '=', 'out_invoice'),
             ('invoice_date', '<=', data['end_date']),
             ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")

        vendor_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id),
             ('partner_id', '=', data['partner_id']),
             ('move_type', '=', 'in_invoice'),
             ('invoice_date', '<=', data['end_date']),
             ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")

        pdc_data= self.env['pdc.wizard'].search(
            [('company_id', '=', self.env.company.id),
             ('partner_id', '=', data['partner_id']),
             ('payment_date', '<=', data['end_date']),
             ('state', 'in',['registered', 'deposited','done']),
             ],
            )

        data_dict = {}
        if rec_data:
            for rec in rec_data:
                pdc_ids = rec.pdc_payment_ids.filtered(
                    lambda x: x.state in ['registered', 'deposited'])
                if not pdc_ids:
                    pdc_ids = rec.pdc_invoices.pdc_id.filtered(
                        lambda x: x.state in ['registered', 'deposited'])

                # print('pdccccccccccccccccccccc',pdc_ids)
                for pdc in pdc_ids:
                    key = pdc.id
                    inv_numbres = ''

                    if pdc.invoice_ids:
                        for inv in pdc.invoice_ids:

                            inv_numbres += inv.name
                            inv_numbres += ','
                    else:
                        for inv in pdc.invoice_pdc_id:
                            inv_numbres += inv.name
                            inv_numbres += ','

                    if key in data_dict:

                        data_dict[key].append({
                            'name': pdc.name,
                            'reference': pdc.reference,
                            'date': pdc.payment_date.strftime('%d/%m/%Y'),
                            'amount': pdc.payment_amount,
                            'invoice_number': inv_numbres,
                        })

                    else:

                        data_dict[key] = [({
                            'name': pdc.name,
                            'reference': pdc.reference,
                            'date': pdc.payment_date.strftime('%d/%m/%Y'),
                            'amount': pdc.payment_amount,
                            'invoice_number': inv_numbres,
                        })]

        vendor_dict = {}
        if vendor_data:
            for rec in vendor_data:
                pdc_ids = rec.pdc_payment_ids.filtered(
                    lambda x: x.state in ['registered', 'deposited',])
                if not pdc_ids:
                    rec.pdc_invoices.pdc_id.filtered(
                        lambda x: x.state in ['registered', 'deposited', ])


                for pdc in pdc_ids:
                    key = pdc.id
                    inv_numbres = ''

                    if pdc.invoice_ids:
                        for inv in pdc.invoice_ids:
                            inv_numbres += inv.name
                            inv_numbres += ','
                    else:
                        for inv in pdc.invoice_pdc_id:
                            inv_numbres += inv.name
                            inv_numbres += ','

                    if key in data_dict:

                        data_dict[key].append({
                            'name': pdc.name,
                            'reference': pdc.reference,
                            'date': pdc.payment_date.strftime('%d/%m/%Y'),
                            'amount': pdc.payment_amount,
                            'invoice_number': inv_numbres,
                        })

                    else:

                        data_dict[key] = [({
                            'name': pdc.name,
                            'reference': pdc.reference,
                            'date': pdc.payment_date.strftime('%d/%m/%Y'),
                            'amount': pdc.payment_amount,
                            'invoice_number': inv_numbres,
                        })]
        pdc_dict = {}
        if pdc_data:

            for data in pdc_data:
                for rec in data.rec_data:
                    rec.initial = True
                    key = data.id
                    inv_numbres = ''
                    inv_numbres += rec.move_name


                    if key in pdc_dict:
                        pdc_dict[key].append({
                            'move_name': rec.name,
                            'amount': data.payment_amount,
                            'date': rec.date.strftime('%d/%m/%Y'),
                            'reference': data.reference,
                            'invoice_number': rec.move_name,
                        })
                    else:
                        pdc_dict[key] = [({
                            'move_name': rec.name,
                            'amount': data.payment_amount,
                            'reference': data.reference,
                            'invoice_number': rec.move_name,
                            'date': rec.date.strftime('%d/%m/%Y'),
                        })]

        new_data_dict = []

        for new_rec in data_dict:
            new_data_dict.append(data_dict[new_rec][0])
        if pdc_data:
            for pdc_rec in pdc_dict:
                new_data_dict.append(pdc_dict[pdc_rec][0])
        # print('new ata',new_data_dict)
        return new_data_dict
    # def _get_cash_details(self, data):
    #     rec_data = self.env['account.move'].search(
    #         [('company_id', '=', self.env.company.id),
    #          ('partner_id', '=', data['partner_id']),
    #          ('move_type', '=', 'out_invoice'),
    #          ('invoice_date', '<=', data['end_date']),
    #          ('state', '=', 'posted'),
    #          ('payment_state', 'in', ['paid'])],
    #         order="invoice_date asc")
    #
    #     data_dict = {}
    #     for rec in rec_data:
    #         ppch_ids = rec.env['account.payment'].search(
    #             [('ref', '=', rec.name),
    #              ])
    #         for ppch in ppch_ids:
    #             print('ppch',ppch)
    #             key = ppch.id
    #             inv_numbres = ''
    #
    #             # for inv in ppch.invoice_ids:
    #             #     inv_numbres += inv.name
    #             #     inv_numbres += ','
    #
    #             if key in data_dict:
    #
    #                 data_dict[key].append({
    #                     'name': ppch.name,
    #
    #                     'date': ppch.strftime('%d/%m/%Y'),
    #                     'amount': ppch.amount,
    #                     'invoice_number': ppch.ref,
    #                 })
    #
    #             else:
    #
    #                 data_dict[key] = [({
    #                     'name': ppch.name,
    #
    #                     'date': ppch.date.strftime('%d/%m/%Y'),
    #                     'amount': ppch.amount,
    #                     'invoice_number': ppch.ref,
    #                 })]
    #
    #     new_data_dict = []
    #     for new_rec in data_dict:
    #         new_data_dict.append(data_dict[new_rec][0])
    #
    #     return new_data_dict
    # def get_invoices_data(self):
    #     params =data
    #     rec_data = self.env['account.move'].search([('company_id', '=', self.env.company.id),
    #                                                 ('partner_id', '=', data['partner_id']),
    #                                                 ('move_type', '=', 'out_invoice'),
    #                                                 ('invoice_date', '<=', data['end_date']),
    #                                                 ('state', '=', 'posted'),
    #                                                 ('payment_state', 'in', ['not_paid', 'partial'])],
    #                                                order="invoice_date asc")
    #
    #     data_dict = {}
    #
    #     for rec in rec_data:
    #         pdc_amt = 0
    #         value = 0
    #         for pdc in rec.pdc_invoices:
    #             # if rec.pdc_payment_ids:
    #             #     pdc_invoice = pdc.invoice_ids.filtered(lambda x: x.id == rec.id)
    #             # if not pdc_invoice:
    #             #     pdc_invoice = pdc.invoice_pdc_id
    #
    #             # for record in pdc.invoice_pdc_id:
    #             #     value = record.amount_residual
    #             # print('hhhhhhhhh',pdc_invoice)
    #             #     for inv in pdc_invoice:
    #             #         pdc_amt = round(inv.amount, 2)
    #             #         print('jjjjaaaaahhh',inv.amount,inv.name,inv.amount_residual)
    #
    #             if not pdc_ids:
    #                 # print("not pdc",rec)
    #                 if rec.amount_residual_signed != 0:
    #                     key = rec.invoice_date.strftime("%B-%Y")
    #                     if key in data_dict:
    #                         data_dict[key].append({
    #                             'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
    #                             'invoice_no': rec.name,
    #                             'lpo_no': rec.lpo_number,
    #                             'do_no': rec.ref,
    #                             'site_name': rec.job_no,
    #                             'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
    #                             'due_amount': rec.amount_residual,
    #
    #                         })
    #                     else:
    #                         data_dict[key] = [
    #                             {
    #                                 'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
    #                                 'invoice_no': rec.name,
    #                                 'lpo_no': rec.lpo_number,
    #                                 'do_no': rec.ref,
    #                                 'site_name': rec.job_no,
    #                                 'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
    #                                 'due_amount': rec.amount_residual,
    #
    #                             }
    #                         ]
    #
    #             else:
    #                 if rec.amount_residual_signed != 0 and abs(rec.amount_residual - pdc_amt) > 0:
    #                     key = rec.invoice_date.strftime("%B-%Y")
    #                     print('due amountttttttttttttttt', abs(rec.amount_residual))
    #                     print('pdc amountttttttttttttttt', abs(pdc_amt))
    #
    #                     if key in data_dict:
    #                         data_dict[key].append({
    #                             'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
    #                             'invoice_no': rec.name,
    #                             'lpo_no': rec.lpo_number,
    #                             'do_no': rec.ref,
    #                             'site_name': rec.job_no,
    #                             'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
    #                             'due_amount': abs(pdc.amount_residual),
    #                         })
    #                     else:
    #                         data_dict[key] = [
    #                             {
    #                                 'invoice_date': rec.invoice_date.strftime(
    #                                     '%d/%m/%Y'),
    #                                 'invoice_no': rec.name,
    #                                 'lpo_no': rec.lpo_number,
    #                                 'do_no': rec.ref,
    #                                 'site_name': rec.job_no,
    #                                 'due_date': rec.invoice_date_due.strftime(
    #                                     '%d/%m/%Y'),
    #                                 'due_amount': abs(pdc.amount_residual),
    #
    #                             }
    #                         ]

    def _get_statement_details(self, data):
        parms = data
        rec_data = self.env['account.move'].search([('company_id', '=', self.env.company.id),
                                                    ('partner_id', '=', data['partner_id']),
                                                    ('move_type', '=', 'out_invoice'),
                                                    ('invoice_date', '<=', data['end_date']),
                                                    ('state', '=', 'posted'),
                                                    ('payment_state', 'in', ['not_paid', 'partial'])],
                                                   order="invoice_date asc")

        data_dict = {}

        for rec in rec_data:
            # if rec.show_del_order == False:
            #     del_num = rec.delivery_order
            # elif rec.show_del_order == True:
            #     del_num = rec.related_del_id.name
            # print(rec.related_sale_id)
            # if rec.move_type == 'out_invoice':
            #     order_no = rec.related_sale_id.name
            # elif rec.move_type == 'in_invoice':
            #     order_no = rec.invoice_origin
            #     print(order_no)
            # else:
            #     order_no = None
            pdc_ids = rec.pdc_payment_ids.filtered(lambda x: x.state in ['registered', 'deposited'])
            pdc_amt = 0
            for pdc in pdc_ids:
                pdc_invoice = pdc.invoice_ids.filtered(lambda x: x.id == rec.id)
                for inv in pdc_invoice:
                    pdc_amt = round(inv.amount, 2)
            if not pdc_ids and rec.pdc_invoices:

                for pdc in rec.pdc_invoices:
                        existing_data = self.env['invoice.pdc.line'].search([
                        ('partner_id', '=', data['partner_id']),
                        ('name', '=', rec.name),
                        ('pdc_id.state', 'in', ['registered','deposited'])], order='id desc', limit=1)
                        # print('working ifffff', abs(pdc.amount_residual),)
                        print('exist name', existing_data.name, 'due', existing_data.amount_residual, 'amount',
                              existing_data.amount, 'partial', existing_data.invoice_partial_amt)
                        tolerance = 1e-10
                        if abs(existing_data.amount_residual) < tolerance:
                            print('=====================////////////////////////',existing_data.amount_residual)
                            existing_data.amount_residual = 0

                        if existing_data.amount_residual != 0  :


                            key = rec.invoice_date.strftime("%B-%Y")
                            if key in data_dict:
                                data_dict[key].append({
                                    'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                                    'invoice_no': rec.name,
                                    'lpo_no': rec.lpo_number,
                                    'do_no': rec.ref,
                                    'site_name': rec.job_no,
                                    'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                                    'due_amount': abs(existing_data.amount_residual),
                                })
                            else:
                                data_dict[key] = [
                                    {
                                        'invoice_date': rec.invoice_date.strftime(
                                            '%d/%m/%Y'),
                                        'invoice_no': rec.name,
                                        'lpo_no': rec.lpo_number,
                                        'do_no': rec.ref,
                                        'site_name': rec.job_no,
                                        'due_date': rec.invoice_date_due.strftime(
                                            '%d/%m/%Y'),
                                        'due_amount': abs(existing_data.amount_residual),

                                    }
                                ]

            elif pdc_ids:
                    # print('working',abs(rec.amount_residual), 'pdc amt',abs(pdc_amt))
                    if rec.amount_residual_signed != 0 and abs(rec.amount_residual - pdc_amt) > 0:
                        key = rec.invoice_date.strftime("%B-%Y")
                        if key in data_dict:
                            data_dict[key].append({
                                'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                                'invoice_no': rec.name,
                                'lpo_no': rec.lpo_number,
                                'do_no': rec.ref,
                                'site_name': rec.job_no,
                                'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                                'due_amount': abs(rec.amount_residual - pdc_amt),
                            })
                        else:
                            data_dict[key] = [
                                {
                                    'invoice_date': rec.invoice_date.strftime(
                                        '%d/%m/%Y'),
                                    'invoice_no': rec.name,
                                    'lpo_no': rec.lpo_number,
                                    'do_no': rec.ref,
                                    'site_name': rec.job_no,
                                    'due_date': rec.invoice_date_due.strftime(
                                        '%d/%m/%Y'),
                                    'due_amount': abs(rec.amount_residual - pdc_amt) ,

                                }
                            ]
            else:

                    # print("working eelse",rec.amount_residual)
                    if rec.amount_residual_signed != 0:
                        key = rec.invoice_date.strftime("%B-%Y")
                        if key in data_dict:
                            data_dict[key].append({
                                'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                                'invoice_no': rec.name,
                                'lpo_no': rec.lpo_number,
                                'do_no': rec.ref,
                                'site_name': rec.job_no,
                                'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                                'due_amount': rec.amount_residual,

                            })
                        else:
                            data_dict[key] = [
                                {
                                    'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                                    'invoice_no': rec.name,
                                    'lpo_no': rec.lpo_number,
                                    'do_no': rec.ref,
                                    'site_name': rec.job_no,
                                    'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                                    'due_amount': rec.amount_residual,

                                }
                            ]

        total_amount = 0
        # print("date_dict :",data_dict)
        for data in data_dict:
            sl = 1
            for list in data_dict[data]:
                list['sl'] = sl
                sl += 1
                total_amount += list['due_amount']
                # print(" total_amount :",total_amount)
        data_dict['total_amount'] = total_amount


        entry = self._get_entries_ret(parms)
        if entry == 'true':
            jrnls = self._get_journal_entries_details(parms)
            total = 0
            for rec in jrnls:
                # print(rec,'33333333333333333333333333')
                total += rec['entry_amount']
                # print(total,'uuuuuu')
            data_dict['total_amount'] += total
        # print("data_dict :",data_dict)
        return data_dict

    def _get_vendor_bill_details(self, data):
        rec_data = self.env['account.move'].search([('company_id', '=', self.env.company.id),
                                                    ('partner_id', '=', data['partner_id']),
                                                    ('invoice_date', '<=', data['end_date']),
                                                    ('move_type', '=', 'in_invoice'),
                                                    ('state', '=', 'posted'),
                                                    ('payment_state', 'in', ['not_paid', 'partial'])],
                                                   order="invoice_date asc")
        data_dict = {}

        for rec in rec_data:
            # if rec.show_del_order == False:
            #     del_num = rec.delivery_order
            # elif rec.show_del_order == True:
            #     del_num = rec.related_del_id.name
            pdc_ids = rec.pdc_payment_ids.filtered(lambda x: x.state in ['registered', 'deposited'])
            if not pdc_ids:
                # print("not pdc", rec)
                if rec.amount_residual != 0:
                    key = rec.invoice_date.strftime("%B-%Y")
                    if key in data_dict:
                        data_dict[key].append({
                            'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                            'invoice_no': rec.name,
                            'lpo_no': rec.lpo_number,
                            'do_no': rec.ref,
                            'site_name': rec.job_no,
                            'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                            'due_amount': abs(rec.amount_residual),

                        })
                    else:
                        data_dict[key] = [
                            {
                                'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                                'invoice_no': rec.name,

                                'lpo_no': rec.lpo_number,
                                'do_no': rec.ref,
                                'site_name': rec.job_no,
                                'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                                'due_amount': abs(rec.amount_residual),

                            }
                        ]
            else:
                # print("elseeeeeeeeeeeeeeeeeeeeeeeeeee")
                if not rec.total_pdc_payment == rec.amount_total:
                    # print("gggggggggggggggggggggg",rec.total_pdc_payment)
                    # print("gggggggggggggggggggggg",rec.amount_total)
                    key = rec.invoice_date.strftime("%B-%Y")
                    if key in data_dict:
                        data_dict[key].append({
                            'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                            'invoice_no': rec.name,
                            'lpo_no': rec.lpo_number,
                            'do_no': rec.ref,
                            'site_name': rec.job_no,
                            'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                            'due_amount': abs(rec.amount_residual),

                        })
                    else:
                        data_dict[key] = [
                            {
                                'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                                'invoice_no': rec.name,

                                'lpo_no': rec.lpo_number,
                                'do_no': rec.ref,
                                'site_name': rec.job_no,
                                'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                                'due_amount': abs(rec.amount_residual),

                            }
                        ]

        total_amount = 0
        for data in data_dict:
            sl = 1
            for list in data_dict[data]:
                list['sl'] = sl
                sl += 1
                total_amount += list['due_amount']
        data_dict['total_amount'] = total_amount
        return data_dict

    def _get_entry_total(self, data):

        entri_data = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('move_id.move_type', '=', 'entry'),
             ('move_id.journal_id.type', 'in', ['general', 'sale']),
             ])
        vendor_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id), ('partner_id', '=', data['partner_id']),
             ('invoice_date', '<=', data['end_date']),
             ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")

        customer_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id), ('partner_id', '=', data['partner_id']),
             ('move_type', '=', 'out_invoice'), ('invoice_date', '<=', data['end_date']), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")

        entry_tot = 0
        vendor_tot = 0
        customer_tot = 0
        # ppc_tot = 0
        pdc_tot = 0
        # ppch_dtls = self._get_cash_details(data)
        pdc_dtls = self._get_pdc_details(data)


        # for ppc in ppch_dtls:
        #
        #     ppc_tot += ppc['amount']


        for pdc in pdc_dtls:
            pdc_tot += pdc['amount']

        jrnls = self._get_journal_entries_details(data)
        total = 0
        for rec in jrnls:
            total += rec['entry_amount']


        for rec in customer_data:
            customer_tot += rec.amount_residual


        for rec in vendor_data:
            vendor_tot += rec.amount_residual
        grand_tot = customer_tot - vendor_tot + total
        grand_tot +=  pdc_tot
        # print("grand_total1",grand_tot)
        return grand_tot

    def _get_total(self, data):
        vendor_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id), ('partner_id', '=', data['partner_id']),
             ('invoice_date', '<=', data['end_date']),
             ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")
        customer_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id), ('partner_id', '=', data['partner_id']),
             ('move_type', '=', 'out_invoice'), ('invoice_date', '<=', data['end_date']), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")

        vendor_tot = 0
        customer_tot = 0
        pdc_tot = 0
        # ppc_tot = 0

        pdc_dtls = self._get_pdc_details(data)
        # ppch_dtls = self._get_cash_details(data)

        inv_dtls = self._get_statement_details(data)
        vendor_dtls = self._get_vendor_bill_details(data)
        if vendor_dtls:
            vendor_tot = vendor_dtls['total_amount']
            # print("vendor_tot :",vendor_tot)

        if inv_dtls:
            customer_tot = inv_dtls['total_amount']
            # print('customer',customer_tot)


        for pdc in pdc_dtls:
            pdc_tot += pdc['amount']
#             print('pdc_tot',pdc_tot)

        # for ppc in ppch_dtls:
        #     ppc_tot += ppc['amount']
        #     print('ppc_tot',ppc_tot)


        # for rec in customer_data:
        #     customer_tot += rec.amount_residual

        # for rec in vendor_data:
        #     vendor_tot += rec.amount_residual
        #     print(vendor_tot,'vendor_tot')

        grand_tot = customer_tot - vendor_tot
        # print(grand_tot,'grand_tot')


        total=pdc_tot
        # print(total, "total1")
        grand_total = abs(total) + abs(grand_tot)

#         print(grand_total,"grand_total2")
        return grand_total

    def _get_status(self, data):
        vendor_data = self.env['account.move'].search(
            [('company_id', '=', self.env.company.id), ('partner_id', '=', data['partner_id']),
             ('invoice_date', '<=', data['end_date']),
             ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")

        if vendor_data:
            return 'true'
        else:
            return 'false'

    def _get_journal_entries_details(self, data):

        rec_data = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('move_id.move_type', '=', 'entry'),
             ('move_id.journal_id.type', 'in', ['general', 'sale']),
             ])
        data_dict = {}
        pdc_data = self.env['pdc.wizard'].search(
            [('company_id', '=', self.env.company.id),
             ('partner_id', '=', data['partner_id']),
             ('payment_date', '<=', data['end_date']),

             ],
        )
        for rec in pdc_data:
            for record in rec.rec_data:
                # print(record.initial,'3345676555tttttt')
                total = 0
                total_value = 0
                if record.initial:

                    domain = [
                        ('partner_id', '=', record.partner_id.id),
                        ('state', 'in', ('registered', 'deposited','done')),
                        ('payment_pdc', '=', 'journal_boolean'),
                    ]
                    records = self.env['pdc.wizard'].search(domain, order='write_date DESC')
                    if records:
                        total_initial_amount = sum(rec.payment_amount for rec in records)
                        for pdc in records.rec_data:
                            if pdc.credit:
                                total_value += pdc.credit
                            elif pdc.debit:
                                total_value += pdc.debit
                        data_dict = [{
                            'entry_date': record.move_id.date.strftime('%d/%m/%Y'),
                            'entry_no': record.move_id.name,
                            'entry_amount': total_value - total_initial_amount,
                        }]
                    else:
                        domain = [
                            ('partner_id', '=', record.partner_id.id),
                            ('state', 'in', ('bounced', 'returned')),
                        ]
                        records = self.env['pdc.wizard'].search(domain, order='write_date DESC')
                        if records:
                            last_edited_record = records[0]
                            total_initial_amount = last_edited_record.payment_amount + last_edited_record.initial_amount
                            data_dict = [{
                                'entry_date': record.move_id.date.strftime('%d/%m/%Y'),
                                'entry_no': record.move_id.name,
                                'entry_amount':total_initial_amount,
                            }]


        for record in rec_data:

            if not record.initial:
                # print('3345676555')
                # rec_data.move_id.print_ini45,000.00tial = True
                if record.account_id.user_type_id.type == 'receivable':
                    data_dict = [{
                        'entry_date': record.move_id.date.strftime('%d/%m/%Y'),
                        'entry_no': record.move_id.name,
                        'entry_amount': record.debit,

                    }]
                elif record.account_id.user_type_id.type == 'payable':
                    data_dict = [
                        {
                            'entry_date': record.move_id.date.strftime('%d/%m/%Y'),
                            'entry_no': record.move_id.name,
                            'entry_amount': record.credit,

                        }
                    ]


        total_amount = 0
        sl = 1

        for list in data_dict:
            list['sl'] = sl
            sl += 1
        return data_dict

    def _get_entries_ret(self, data):
        entri_data = self.env['account.move.line'].search(
            [('partner_id', '=', data['partner_id']), ('move_id.move_type', '=', 'entry'),
             ('move_id.journal_id.type', '=', 'general'),
             ])
        if entri_data:
            return 'true'
        else:
            return 'false'