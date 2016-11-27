# -*- coding: utf-8 -*-

{
    'name': 'LiqPay Payment Acquirer Split Rules',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: LiqPay Split Rules',
    'version': '1.3',
    'license': 'OPL-1',
    'price': 50.00,
    'currency': 'EUR',
    'author': 'ERP Ukraine',
    'website': 'https://erp.co.ua',
    'description': """LiqPay Payment Acquirer Split Rules.
Payment will be split across couple receivers.""",
    'depends': ['payment', 'website_sale', 'event_sale', 'payment_liqpay'],
    'data': [
        'views/payment_liqpay.xml',
    ],
    'installable': True,
    'auto_install': False,
}
