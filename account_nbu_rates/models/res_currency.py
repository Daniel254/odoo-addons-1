# -*- coding: utf-8 -*-

import logging

import requests

from openerp import api, fields, models
_logger = logging.getLogger(__name__)


class CurrencyRate(models.Model):

    _inherit = 'res.currency.rate'

    # Add more precision. Original was digits=(12, 6)
    rate = fields.Float(
        'Rate',
        digits=(14, 10),
        help='The rate of the currency to the currency of rate 1')


class Currency(models.Model):

    _inherit = 'res.currency'

    NBU_EX_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'

    @api.model
    def _get_current_rate(self):
        res = super(Currency, self)._get_current_rate(
            name=None, arg=None, context=self._context)
        for rec in self:
            rec.rate = res[rec.id]
        return res

    # Add more precision. Original was digits=(12, 6)
    rate = fields.Float(
        'Current Rate',
        compute=_get_current_rate,
        digits=(14, 10),
        help='The rate of the currency to the currency of rate 1.')

    @api.model
    def _update_nbu_rates(self):
        date = self._context.get('date') or fields.Date.today()
        companies = self.env['res.company'].search([])
        for company in companies:
            uah_ccy = self.env['res.currency'].search([
                ('name', '=', 'UAH'),
                ('active', '=', True)])
            if not uah_ccy:
                _logger.warn('UAH currency is not Active')
                return False
            if uah_ccy.rate != 1.0:
                _logger.info('UAH currency rate is not 1. Fixing this...')
                self.env['res.currency.rate'].create({
                    'currency_id': uah_ccy.id,
                    'rate': 1.0,
                    'name': date,
                    'company_id': company.id,
                })
                if uah_ccy.rate != 1.0:
                    _logger.info('Giving up...')
                    return False
                else:
                    _logger.info('UAH currency rate is 1')

            active_ccys = self.env['res.currency'].search([
                ('name', '!=', 'UAH'),
                ('active', '=', True)])
            for ccy in active_ccys:
                response = [{}]
                params = {
                    'valcode': ccy.name,
                    'date': date[0:4] + date[5:7] + date[8:10],
                    'json': '',
                }
                try:
                    r = requests.get(self.NBU_EX_URL,
                                     params=params,
                                     timeout=30)
                except requests.exceptions.RequestException as e:
                    _logger.warn(e)
                    continue
                try:
                    response = r.json()
                except (ValueError, UnicodeDecodeError):
                    _logger.warn('JSON parsing error')
                    continue
                if r.status_code == 200 and len(response) > 0:
                    if response[0].get('rate', 0) > 0:
                        self.env['res.currency.rate'].create({
                            'currency_id': ccy.id,
                            'rate': uah_ccy.rate / response[0]['rate'],
                            'name': date,
                            'company_id': company.id,
                        })
        return True
