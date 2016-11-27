# -*- coding: utf-8 -*-
{
    'name': 'Ukraine - Payroll',
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'category': 'Localization',
    'depends': ['hr_payroll', 'hr_holidays'],
    'version': '1.3',
    'license': 'OPL-1',
    'price': 50.00,
    'currency': 'EUR',
    'description': """
Заробітна плата для України.
=============================

    * Оклад по днях
    * Тариф по годинах
    * Розрахунок індексації
    * Надбавки фіксовані та відсотком
    * Розрахунок утримань
    * Податкова соціальна пільга
    * ЕСВ на різницю між окладом та МЗП
    * Облік робочого часу: свята, відпустки, лікарняні, прогули.
    * Та багато іншого
    """,

    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'data/leave_types.xml',
        'data/salary_rules_category.xml',
        'data/salary_rules.xml',
        'data/payroll_structure.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payslip_vew.xml',
        'views/hr_payroll_view.xml',
        'views/contrib_registers_view.xml',
    ],
    'installable': True,
    'application': True,
}
