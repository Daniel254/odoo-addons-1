# -*- coding: utf-8 -*-
{
    'name': 'Ukrainian - Payroll with Accounting',
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'category': 'Localization',
    'depends': ['l10n_ua_hr_payroll', 'hr_payroll_account'],
    'version': '1.3',
    'license': 'Other proprietary',
    'price': 50.00,
    'currency': 'EUR',
    'description': """
Бухгалтерські проведення для зарплати (МСФЗ)
==============================================
    """,
    'auto_install': False,
    'demo': [],
    'data': [
        'l10n_ua_hr_payroll_account_data.xml',
    ],
    'installable': True,
    'application': True,
}
