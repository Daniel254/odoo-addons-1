# -*- coding: utf-8 -*-
{
    'name': 'NBU exchange rates sync',
    'author': 'ERP Ukraine',
    'website': 'https://erp.co.ua',
    'summary': u"Sync NBU exchange rates online",
    'category': 'Accounting & Finance',
    'depends': ['account'],
    'version': '1.0',
    'license': 'Other proprietary',
    'price': 50.00,
    'currency': 'EUR',
    'description': """
This module adds cron task to downloads exchange rates from
National Bank of Ukraine on daily basis.
UAH excange rate is set to 1. Other rates are set relatively to UAH.
""",
    'auto_install': False,
    'demo': [],
    'depends': ['account'],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
}
