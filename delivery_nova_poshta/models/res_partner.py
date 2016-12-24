# -*- coding: utf-8 -*-

import logging
from openerp import fields, models, api, _
from openerp.exceptions import UserError

from .npapi2 import NPApi, NPException
import re

_logger = logging.getLogger(__name__)


class NPPartner(models.Model):
    _inherit = 'res.partner'

    is_nova_poshta_addr = fields.Boolean(
        string=u"Адреса для Нової Пошти",
        default=False)

    np_service_type = fields.Selection(
        [
         ('Doors', u"Адреса"),
         ('Warehouse', u"Відділення"),
        ],
        string=u"Тип доставки",
        index=True,
        default='Warehouse')
    np_payer_type = fields.Selection(
        [
         ('Sender', u"Відправник"),
         ('Recipient', u"Одержувач"),
         ('ThirdPerson', u"Третя особа"),
        ],
        string=u"Платник",
        index=True,
        default='Sender')
    np_payment_type = fields.Selection(
        [
         ('Cash', u"Готівка"),
         ('NonCash', u"Через банк"),
        ],
        string=u"Спосіб оплати",
        index=True,
        default='Cash')
    np_cargo_type = fields.Selection(
        [
         ('Cargo', u"Вантаж"),
         ('Documents', u"Документи"),
         ('TiresWheels', u"Шини-диски"),
         ('Pallet', u"Палети"),
        ],
        string=u"Тип вантажу",
        index=True,
        default='Cargo')
    np_role = fields.Selection(
        [
         ('Sender', u"Відправник"),
         ('Recipient', u"Одержувач"),
        ],
        string=u"Роль",
        index=True,
        default='Recipient')

    np_city_id = fields.Many2one(
        'delivery.carrier.np.cities',
        string=u"Місто",)
    np_city_ref = fields.Char(
        related='np_city_id.ref',
        readonly=True)
    np_wh_id = fields.Many2one(
        'delivery.carrier.np.warehouses',
        string=u"Відділеня",
        domain="[('city_ref', '=', np_city_ref)]")
    np_street_id = fields.Many2one(
        'delivery.carrier.np.streets',
        string=u"Вулиця",
        domain="[('city_ref', '=', np_city_ref)]")
    np_building = fields.Char(string=u"Будинок", default='')
    np_flat = fields.Char(string=u"Квартира", default='')
    np_phone = fields.Char(string=u"Телефон")
    np_email = fields.Char(string=u"Ел. пошта")
    np_first_name = fields.Char(string=u"Ім'я")
    np_middle_name = fields.Char(string=u"По-батькові")
    np_last_name = fields.Char(string=u"Прізвище")
    np_countpart_id = fields.Many2one(
        'delivery.carrier.np.counterparties',
        string=u"Контрагент",
        domain="[('cp_property', '=', np_role)]")
    np_countpart_ref = fields.Char(
        related='np_countpart_id.ref',
        readonly=True)
    np_contactpers_id = fields.Many2one(
        'delivery.carrier.np.cpcontactperson',
        string=u"Контактна особа",
        domain="[('cp_ref', '=', np_countpart_ref)]")
    np_cpaddress_id = fields.Many2one(
        'delivery.carrier.np.cpaddress',
        string=u"Адреса контакту",
        domain="[('cp_ref', '=', np_countpart_ref)]")

    @api.model
    def download_np_streets(self, city_ref=''):
        if not city_ref:
            return False
        page = 0
        count = 500
        np_obj = self.env['delivery.carrier.np.streets']
        while count >= 500:
            page += 1
            count = np_obj.cron_update(
                params={
                    'CityRef': city_ref,
                    'Page': str(page)
                    },
                static_ref={'city_ref': city_ref})
        return True

    @api.model
    def download_np_counterparties(self, city_ref='', role=''):
        if not city_ref or not role:
            return False
        np_obj = self.env['delivery.carrier.np.counterparties']
        np_obj.cron_update(
         params={
             'City': city_ref,
             'CounterpartyProperty': role
         },
         static_ref={'cp_property': role})
        return True

    @api.model
    def get_default_cp(self, role=''):
        if not role:
            return None
        np_obj = self.env['delivery.carrier.np.counterparties']
        domain = [
            '|',
            ('city_ref', '=', self.np_city_id.ref),
            ('city_ref', '=', '00000000-0000-0000-0000-000000000000'),
            ('cp_property', '=', role)]
        res = np_obj.search(domain, limit=1)
        if len(res) > 0:
            return res.id
        else:
            return None

    @api.onchange('np_city_id')
    def onchange_np_city_id(self):
        self.np_wh_id = None
        self.np_street_id = None
        self.np_countpart_id = None
        if self.np_city_id:
            self.city = self.np_city_id.name
            self.zip = ''
            self.country_id = None
            # download streets for the current city
            self.download_np_streets(self.np_city_id.ref)
            # download counterparties for the current city
            self.download_np_counterparties(self.np_city_id.ref, self.np_role)
            # assign default counterparty
            self.np_countpart_id = self.get_default_cp(self.np_role)

    @api.onchange('np_countpart_id')
    def onchange_np_countpart_id(self):
        self.np_contactpers_id = None
        self.np_cpaddress_id = None
        if self.np_countpart_id:
            if not self.np_countpart_id.city_ref:
                self.np_countpart_id.city_ref = self.np_city_id.ref

            # download contact persons for the current cp
            np_obj = self.env['delivery.carrier.np.cpcontactperson']
            np_obj.cron_update(
                params={'Ref': self.np_countpart_id.ref},
                static_ref={'cp_ref': self.np_countpart_id.ref})
            # download addresses for the current cp
            np_obj = self.env['delivery.carrier.np.cpaddress']
            is_cust = self.parent_id.customer
            np_obj.cron_update(
             params={
                 'Ref': self.np_countpart_id.ref,
                 'CounterpartyProperty': self.np_role
             },
             static_ref={'cp_ref': self.np_countpart_id.ref})

    @api.onchange('np_role')
    def onchange_np_role(self):
        self.np_countpart_id = None
        self.np_contactpers_id = None
        self.np_cpaddress_id = None

    @api.onchange('np_contactpers_id')
    def onchange_np_contactpers_id(self):
        if self.np_contactpers_id:
            self.name = self.np_contactpers_id.name

    @api.onchange('np_street_id', 'np_building', 'np_flat')
    def onchange_np_street_id(self):
        if self.np_street_id:
            self.street = u"вул. " + self.np_street_id.name
        if self.np_building:
            self.street += u", буд. " + self.np_building
        if self.np_flat:
            self.street += u", кв. " + self.np_flat

    @api.onchange('np_phone')
    def onchange_np_phone(self):
        if self.np_phone:
            self.phone = self.np_phone

    @api.onchange('np_email')
    def onchange_np_email(self):
        if self.np_email:
            self.email = self.np_email

    @api.onchange('np_wh_id')
    def onchange_np_wh_id(self):
        if self.np_wh_id:
            self.street2 = self.np_wh_id.name

    @api.onchange('np_first_name', 'np_last_name', 'np_middle_name')
    def onchange_np_pip(self):
        pip_pattern = u'^[а-яА-ЯіІїЇґҐєЄ’\'"-]+$'
        if self.np_last_name:
            if re.search(pip_pattern, self.np_last_name) is None:
                raise UserError(u"Заповніть прізвище українською")
        if self.np_first_name:
            if re.search(pip_pattern, self.np_first_name) is None:
                raise UserError(u"Заповніть ім’я українською")
        if self.np_middle_name:
            if re.search(pip_pattern, self.np_middle_name) is None:
                raise UserError(u"Заповніть по-батькові українською")

    @api.onchange('np_service_type')
    def onchange_np_service_type(self):
        if self.np_service_type == 'Doors':
            self.street2 = ''
        if self.np_service_type == 'Warehouse':
            self.street = ''

    def _get_cp_ref(self):
        '''
        Search counterparty reference.
        Search cp created on novaposhta site, if none - search default cp.
        If none - download cp table and try again.
        '''
        self.ensure_one()
        np_obj = self.env['delivery.carrier.np.counterparties']
        domain = [
            ('city_ref', '=', self.np_city_id.ref),
            ('cp_property', '=', self.np_role)]
        res = np_obj.search(domain, limit=1)
        if len(res) <= 0:   # search deafult cp
            domain = [
                ('city_ref', '=', '00000000-0000-0000-0000-000000000000'),
                ('cp_property', '=', self.np_role)]
            res = np_obj.search(domain, limit=1)
        if len(res) > 0:
            self.np_countpart_id = res.id
            if not self.np_countpart_id.city_ref:
                self.np_countpart_id.city_ref = self.np_city_id.ref
            return res.ref
        else:
            # download counterparties for the current city
            self.download_np_counterparties(self.np_city_id.ref, self.np_role)
            domain = [
                ('city_ref', '=', self.np_city_id.ref),
                ('cp_property', '=', self.np_role)]
            res = np_obj.search(domain, limit=1)
            if len(res) <= 0:   # search deafult cp
                domain = [
                    ('city_ref', '=', '00000000-0000-0000-0000-000000000000'),
                    ('cp_property', '=', self.np_role)]
                res = np_obj.search(domain, limit=1)
            if len(res) > 0:
                self.np_countpart_id = res.id
                if not self.np_countpart_id.city_ref:
                    self.np_countpart_id.city_ref = self.np_city_id.ref
                return res.ref
            return None

    def _get_cp_address(self):
        self.ensure_one()
        if self.np_service_type == 'Warehouse':
            return self.np_wh_id.ref
        else:
            api_key = self.env['delivery.carrier.np.model']._get_np_api_key()
            try:
                np_api = NPApi(api_key)
                if not api_key:
                    _logger.warn('No API key')
                    return
                methodProperties = {
                    'CounterpartyRef': self._get_cp_ref(),
                    'StreetRef': self.np_street_id.ref,
                    'BuildingNumber': self.np_building or '',
                    'Flat': self.np_flat or '',
                    'Note': ''
                }
                res = np_api.Address.save(methodProperties)
                return res[0]['Ref']
            except NPException, e:
                _logger.warn('Nova Poshta API exception')

    def _get_cp_contact(self):
        self.ensure_one()
        api_key = self.env['delivery.carrier.np.model']._get_np_api_key()
        try:
            np_api = NPApi(api_key)
            if not api_key:
                _logger.warn('No API key')
                return
            methodProperties = {
                'FirstName': self.np_first_name,
                'LastName': self.np_last_name,
                'MiddleName': self.np_middle_name,
                'Phone': self.np_phone,
                'Email': self.email or '',
                'CounterpartyRef': self._get_cp_ref(),
            }
            res = np_api.ContactPerson.save(methodProperties)
            return res[0]['Ref']
        except NPException, e:
            _logger.warn('Nova Poshta API exception')
