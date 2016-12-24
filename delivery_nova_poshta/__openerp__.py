# -*- coding: utf-8 -*-

{
    'name': 'Nova Poshta Shipping Integration',
    'category': 'Sales Management',
    'summary': 'Odoo - Nova Poshta Shipping Integration',
    'version': '1.1',
    'license': 'Other proprietary',
    'price': 50.00,
    'currency': 'EUR',
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'depends': ['delivery'],
    'data': [
        'views/np_delivery_carrier.xml',
        'views/res_partner.xml',
        'data/np_models_data.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}
