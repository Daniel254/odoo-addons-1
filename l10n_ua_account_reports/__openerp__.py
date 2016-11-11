# -*- coding: utf-8 -*-
{
    'name': 'Ukrainian Accounting Reports',
    'author': 'ERP Ukraine',
    'website': 'https://erp.co.ua',
    'category': 'Localization/Account Charts',
    'depends': ['account'],
    'version': '1.1',
    # 'price': 20.00,
    # 'currency': 'EUR',
    'description': """
Друковані форми первинних документів для бухгалтерії
======================================================
Цей модуль встановлює додаткові форми для друку
первинних документів з інтерфейсу бухгалтера.

В меню друку рахунків можна буде вибрати форму накладних та актів,
що відповідє вимогам українських стандартів.
""",
    'auto_install': False,
    'demo': [],
    'data': ['views/acc_report_nakladna.xml',
             'data/account_report.xml'],
    'installable': True
}
