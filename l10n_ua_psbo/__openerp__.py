# -*- coding: utf-8 -*-
{
    'name': u"Ukraine - Accounting PSBO",
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'summary': u"Український бухоблік згідно ПСБО",
    'version': '1.3',
    'license': 'Other proprietary',
    'price': 50.00,
    'currency': 'EUR',
    'description': u"""
Бухгалтерський облік для України (ПСБО)
=======================================

Цей модуль дає можливість вести бухгалтерський
облік діяльності підприємства згідно національних
стандартів фінансової звітності.

Встановлюється типовий план рахунків,
який підійде більшості підприємств.
Також буде створено налаштування податків
для обліку ПДВ
    """,
    'category': 'Localization',
    'version': '1.1',
    'depends': ['account'],
    'data': [
        'partner_view.xml',
        'data/account_chart_template.xml',
        'data/account.account.template.csv',
        'data/account_tax_template.xml',
        'data/account_chart_template_config.xml',
        'data/account_chart_template.yml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
