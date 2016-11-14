# -*- coding: utf-8 -*-
{
    'name': 'Ukrainian Sale Reports',
    'author': 'ERP Ukraine',
    'website': 'https://erp.co.ua',
    'category': 'Sales',
    'depends': ['sale'],
    'version': '1.3',
    # 'price': 20.00,
    # 'currency': 'EUR',
    'description': """
Друковані форми для продажу
=======================================
Цей модуль встановлює додаткові форми для друку комерційної пропозиції
та договору на поставки.
""",
    'auto_install': False,
    'demo': [],
    'data': [
            'views/report_saleorder.xml',
        ],
    'installable': True
}
