# -*- coding: utf-8 -*-

{
    'name': 'Nova Poshta Website Shipping',
    'category': 'Website',
    'summary': 'Nova Poshta Shipping Integration for Website Sales',
    'version': '1.1',
    'license': 'Other proprietary',
    'price': 50.00,
    'currency': 'EUR',
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'depends': ['website_sale_delivery', 'delivery_nova_poshta'],
    'data': [
        'views/templates.xml',
    ],
    'js': ['static/src/js/website_delivery_nova_poshta.js'],
    'application': True,
    'auto_install': False,
    'installable': True,
}
