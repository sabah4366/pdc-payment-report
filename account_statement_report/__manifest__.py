# -*- coding: utf-8 -*-
{
    'name': "Customer Account Statement Report",

    'summary': """
        Customer Account Statement Report""",

    'description': """
        Customer Account Statement Report
    """,

    'author': "AbrusNetworks",
    'website': "https://www.abrusnetworks.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','web','report_xlsx',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/customer_report_wizard_view.xml',
        'views/account_view.xml',
        'report/report_pdf.xml',
        'report/report_statement.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
