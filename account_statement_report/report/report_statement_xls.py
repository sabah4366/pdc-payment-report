from odoo import models
import json
from datetime import datetime
from datetime import date



class CollectionSaleReportXls(models.AbstractModel):
    _name = 'report.account_statement_report.report_statement_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        company_id = self.env['res.company'].browse(data['company'])
        sheet1 = workbook.add_worksheet("Account Statement Report")
        main_head = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'bg_color': '#7f8185',
            'font_color': '#0a0a0a',
            'font_size': 18,
            'bold': 1,
        })

        sub_heading = workbook.add_format({
            'font_size': 8,
            'align': 'vcenter',
            'bold': 1,

        })

        total_head = workbook.add_format({
            'font_size': 8,
            'align': 'vcenter',
            'bold': 1,
            # 'bg_color': '#7C7BADBD',

            'bg_color': '#7f8185',
            'font_color': '#0a0a0a',

        })

        grand_total_head = workbook.add_format({
            'font_size': 8,
            'align': 'vcenter',
            'bold': 1,
            # 'bg_color': '#7C7BADBD',

            'bg_color': '#fce4d6',
            'font_color': '#0a0a0a',

        })

        sub_total_head = workbook.add_format({
            'font_size': 8,
            'align': 'vcenter',
            'bold': 1,
            # 'bg_color': '#7C7BADBD',

            'bg_color': '#9bc2e6;',
            'font_color': '#0a0a0a',

        })



        format2 = workbook.add_format({
            'font_size': 10,
            'align': 'vcenter',
        })

        sheet1.merge_range('B1:G2', "Account Statement", main_head)

        partner_id = self.env['res.partner'].browse(lines.partner_id.id)
        sheet1.set_column(0, 0, 15)
        sheet1.set_column(1, 1, 15)
        sheet1.set_column(2, 2, 15)
        sheet1.set_column(6, 6, 15)
        sheet1.set_column(7, 7, 20)

        sheet1.write(4, 0, 'Customer', sub_heading)
        sheet1.write(4, 1, partner_id.name, sub_heading)
        sheet1.write(5, 0, 'Address', sub_heading)
        sheet1.write(5, 1, partner_id.street, format2)

        rec_data = self.env['account.move'].search(
            [('partner_id', '=', lines.partner_id.id),
             ('invoice_date', '<=', lines.to_date),
             ('company_id', '=', company_id.id),
             ('state', '=', 'posted'),('move_type','=','out_invoice'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")
        entry_data = self.env['account.move.line'].search(
            [('partner_id', '=', lines.partner_id.id), ('move_id.move_type', '=', 'entry'),
             ('move_id.journal_id.type', '=', 'general'),
             ])

        data_dict = {}
        entry_data_dict = {}

        for rec in rec_data:
            pdc_ids = rec.pdc_payment_ids.filtered(
                lambda x: x.state in ['registered', 'deposited'])
            if not pdc_ids:
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

            else:
                if rec.amount_residual - rec.pdc_payment_amount != 0:
                    key = rec.invoice_date.strftime("%B-%Y")
                    if key in data_dict:
                        data_dict[key].append({
                            'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                            'invoice_no': rec.name,
                            'lpo_no': rec.lpo_number,
                            'do_no': rec.ref,
                            'site_name': rec.job_no,
                            'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                            'due_amount': rec.amount_residual - rec.pdc_payment_amount,
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
                                'due_amount': rec.amount_residual - rec.pdc_payment_amount,

                            }
                        ]
        for rec in entry_data:
            # key = rec.invoice_date.strftime("%B-%Y")
            if rec.account_id.user_type_id.type == 'receivable':
                entry_data_dict = [{
                    'entry_date': rec.move_id.date.strftime('%d/%m/%Y'),
                    'entry_no': rec.move_id.name,
                    # 'lpo_no': rec.invoice_origin,
                    # 'do_no': rec.ref,
                    # 'site_name': rec.job_no,
                    # 'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                    'entry_amount': rec.debit,

                }]
            elif rec.account_id.user_type_id.type == 'payable':
                entry_data_dict = [
                    {
                        'entry_date': rec.move_id.date.strftime('%d/%m/%Y'),
                        'entry_no': rec.move_id.name,
                        # 'lpo_no': rec.invoice_origin,
                        # 'do_no': rec.ref,
                        # 'site_name': rec.job_no,
                        # 'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                        'entry_amount': rec.credit,

                    }
                ]
        # return entry_data_dict

        j = 10
        sub_total = 0
        sheet1.write(j, 0, 'SL No', sub_heading)
        sheet1.write(j, 1, 'Invoice Date', sub_heading)
        sheet1.write(j, 2, 'Invoice No', sub_heading)
        sheet1.write(j, 3, 'LPO No', sub_heading)
        sheet1.write(j, 4, 'DO No', sub_heading)
        sheet1.write(j, 5, 'Site Name', sub_heading)
        sheet1.write(j, 6, 'Due Date', sub_heading)
        sheet1.write(j, 7, 'Outstanding Amount', sub_heading)
        j += 1
        t = 0
        entry_total = 0

        for data in entry_data_dict:
            sheet1.write(j, 0, 'Initial Balance', sub_heading)


            sl = 0
            j += 1
            entry_total = 0

            # for vals in entry_data_dict[data]:
            entry_total += data['entry_amount']
            # t = 0
            sl += 1
            sheet1.write(j, t, sl, format2)
            t += 1
            sheet1.write(j, t, data['entry_date'], format2)
            t += 1
            sheet1.write(j, t, data['entry_no'], format2)
            t += 1
            sheet1.write(j, t,'',  format2)
            t += 1
            sheet1.write(j, t,'',  format2)
            t += 1
            sheet1.write(j, t,'',  format2)
            t += 1
            sheet1.write(j, t,'',  format2)
            t += 1
            sheet1.write(j, t, '{0:,.3f}'.format(data['entry_amount']) if company_id.is_oman_company else '{0:,.2f}'.format(data['entry_amount']), format2)
            j += 1

        j += 2

        for data in data_dict:
            sheet1.write(j, 0, data, sub_heading)


            sl = 0
            j += 1
            month_total = 0

            for vals in data_dict[data]:
                month_total += vals['due_amount']
                t = 0
                sl += 1
                sheet1.write(j, t, sl, format2)
                t += 1
                sheet1.write(j, t, vals['invoice_date'], format2)
                t += 1
                sheet1.write(j, t, vals['invoice_no'], format2)
                t += 1
                sheet1.write(j, t, vals['lpo_no'], format2)
                t += 1
                sheet1.write(j, t, vals['do_no'], format2)
                t += 1
                sheet1.write(j, t, vals['site_name'], format2)
                t += 1
                sheet1.write(j, t, vals['due_date'], format2)
                t += 1
                sheet1.write(j, t, '{0:,.3f}'.format(vals['due_amount'])  if company_id.is_oman_company else '{0:,.2f}'.format(vals['due_amount']), format2)
                j += 1
            sheet1.write(j, t-1, 'Total', total_head)
            sheet1.write(j, t,  '{0:,.3f}'.format(month_total) if company_id.is_oman_company else  '{0:,.2f}'.format(month_total) , total_head)
            j += 2
            sub_total += month_total
        enrt_tot = 0
        for data in entry_data_dict:
            enrt_tot +=data['entry_amount']

        sheet1.write(j, 6, 'Sub Total', sub_total_head)
        sheet1.write(j, 7, '{0:,.3f}'.format(sub_total + entry_total) if company_id.is_oman_company else '{0:,.2f}'.format(sub_total + entry_total), sub_total_head)
        j += 2




        data_dict = {}

        for rec in rec_data:
            pdc_ids = rec.pdc_payment_ids.filtered(
                lambda x: x.state in ['registered', 'deposited'])
            for pdc in pdc_ids:
                key = pdc.id
                inv_numbres = ''

                for inv in pdc.invoice_ids:
                    inv_numbres += inv.name
                    inv_numbres += ','

                if key in data_dict:

                    data_dict[key].append({
                        'reference': pdc.reference,
                        'name': pdc.name,
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
        new_data_dict = []
        for new_rec in data_dict:
            new_data_dict.append(data_dict[new_rec][0])



        vendor_data = self.env['account.move'].search(
            [('partner_id', '=', lines.partner_id.id),
             ('invoice_date', '<=', lines.to_date),
             ('company_id', '=', company_id.id),
             ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid', 'partial'])],
            order="invoice_date asc")
        if vendor_data:
            sheet1.write(j, 0, 'Purchase for Materials', sub_heading)
            j += 2

        vendor_dict = {}

        vendor_sub_total = 0


        for rec in vendor_data:
            key = rec.invoice_date.strftime("%B-%Y")
            if key in vendor_dict:
                vendor_dict[key].append({
                    'invoice_date': rec.invoice_date.strftime('%d/%m/%Y'),
                    'invoice_no': rec.name,
                    'lpo_no': rec.lpo_number,
                    'do_no': rec.ref,
                    'site_name': rec.job_no,
                    'due_date': rec.invoice_date_due.strftime('%d/%m/%Y'),
                    'due_amount': rec.amount_residual,

                })
            else:
                vendor_dict[key] = [
                    {
                        'invoice_date': rec.invoice_date.strftime(
                            '%d/%m/%Y'),
                        'invoice_no': rec.name,
                        'lpo_no': rec.lpo_number,
                        'do_no': rec.ref,
                        'site_name': rec.job_no,
                        'due_date': rec.invoice_date_due.strftime(
                            '%d/%m/%Y'),
                        'due_amount': rec.amount_residual,

                    }
                ]
        if vendor_data:
            for data in vendor_dict:
                sheet1.write(j, 0, data, sub_heading)

                sl = 0
                j += 1
                vendor_month_total = 0

                for vals in vendor_dict[data]:
                    vendor_month_total += vals['due_amount']
                    t = 0
                    sl += 1
                    sheet1.write(j, t, sl, format2)
                    t += 1
                    sheet1.write(j, t, vals['invoice_date'], format2)
                    t += 1
                    sheet1.write(j, t, vals['invoice_no'], format2)
                    t += 1
                    sheet1.write(j, t, vals['lpo_no'], format2)
                    t += 1
                    sheet1.write(j, t, vals['do_no'], format2)
                    t += 1
                    sheet1.write(j, t, vals['site_name'], format2)
                    t += 1
                    sheet1.write(j, t, vals['due_date'], format2)
                    t += 1
                    sheet1.write(j, t, '{0:,.3f}'.format(vals['due_amount']) if company_id.is_oman_company else '{0:,.2f}'.format(vals['due_amount']) ,
                                 format2)
                    j += 1
                sheet1.write(j, 6, 'Total', total_head)
                sheet1.write(j, 7, '{0:,.3f}'.format(vendor_month_total) if company_id.is_oman_company else '{0:,.2f}'.format(vendor_month_total), total_head)
                j += 2
                vendor_sub_total += vendor_month_total
            sheet1.write(j, 6, 'Sub Total', sub_total_head)
            sheet1.write(j, 7, '{0:,.3f}'.format(vendor_sub_total)  if company_id.is_oman_company else '{0:,.2f}'.format(vendor_sub_total), sub_total_head)
            j += 2

        pdc_sub_total = 0

        if new_data_dict:
            sheet1.write(j, 0, 'PDC DETAILS', sub_heading)

            j += 2
            sl = 0

            sheet1.write(j, 0, 'Sl No', sub_heading)
            sheet1.write(j, 1, 'Cheque No', sub_heading)
            sheet1.write(j, 2, 'Invoice No', sub_heading)
            sheet1.write(j, 3, 'Cheque Date', sub_heading)
            sheet1.write(j, 4, 'Cheque Amount', sub_heading)
            j += 1


            for pdc in new_data_dict:
                pdc_sub_total += pdc['amount']
                t = 0
                sl += 1
                sheet1.write(j, t, sl, format2)
                t += 1
                sheet1.write(j, t, pdc['name'], format2)
                t += 1
                sheet1.write(j, t, pdc['invoice_number'], format2)
                t += 1
                sheet1.write(j, t, pdc['date'], format2)
                t += 1
                sheet1.write(j, t, '{0:,.3f}'.format(pdc[
                                                         'amount']) if company_id.is_oman_company else '{0:,.2f}'.format(
                    pdc['amount']),
                             format2)
                j += 1
            sheet1.write(j, 4, 'Total', total_head)
            sheet1.write(j, 5, '{0:,.3f}'.format(
                pdc_sub_total) if company_id.is_oman_company else '{0:,.2f}'.format(
                pdc_sub_total), total_head)
            j += 2

        j += 3


        if entry_data:
            sheet1.write(j, 6, 'Grand Total', grand_total_head)
            sheet1.write(j, 7, '{0:,.3f}'.format(sub_total - vendor_sub_total + entry_total + pdc_sub_total)  if company_id.is_oman_company else '{0:,.2f}'.format(sub_total - vendor_sub_total + entry_total + pdc_sub_total) , grand_total_head)
            total_amount = '{0:,.3f}'.format(sub_total - vendor_sub_total + entry_total + pdc_sub_total)  if company_id.is_oman_company else '{0:,.2f}'.format(sub_total - vendor_sub_total + entry_total + pdc_sub_total)
        else:
            sheet1.write(j, 6, 'Grand Total', grand_total_head)
            sheet1.write(j, 7, '{0:,.3f}'.format(sub_total - vendor_sub_total + pdc_sub_total ) if company_id.is_oman_company else '{0:,.2f}'.format(sub_total - vendor_sub_total + pdc_sub_total) , grand_total_head)
            total_amount = '{0:,.3f}'.format(sub_total - vendor_sub_total + pdc_sub_total ) if company_id.is_oman_company else '{0:,.2f}'.format(sub_total - vendor_sub_total + pdc_sub_total)
        sheet1.merge_range('A8:K8', 'Below is the current statement of your account. The total amount due is ' + str(company_id.currency_id.name) + ' ' + str(total_amount) + ' as on '+ str(lines.to_date)+' and the list of outstanding invoices are listed below.', format2)

        sheet1.merge_range('A9:I9', 'In case of any queries or clarifications please feel free to call us on '+ str(company_id.phone) + ' or email us on ' + str(company_id.email), format2)



