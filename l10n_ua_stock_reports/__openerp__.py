# -*- coding: utf-8 -*-
{
    'name': 'Ukrainian Stock Reports',
    'author': 'ERP Ukraine',
    'website': 'https://erp.co.ua',
    'category': 'Inventory Management',
    'depends': ['stock'],
    'version': '1.2',
    'license': 'OPL-1',
    'price': 50.00,
    'currency': 'EUR',
    'description': """
Друковані форми для складськго обліку
=======================================
Цей модуль встановлює додаткові форми для друку складських документів.

В меню друку операцій переміщення товарів можна буде вибрати форму
накладних, що відповідє вимогам Українських стандартів.
""",
    'auto_install': False,
    'demo': [],
    'data': ['views/report_nakladna.xml',
             'data/stock_report.xml'],
    'installable': True,
    'application': True,
}
