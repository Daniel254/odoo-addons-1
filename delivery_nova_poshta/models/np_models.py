# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning

from datetime import datetime
import logging

from npapi2 import NPApi, NPException

_logger = logging.getLogger(__name__)


class NPModel(models.AbstractModel):
    _name = 'delivery.carrier.np.model'

    _np_key = 'ref'

    def _get_np_api_key(self):
        domain = [('delivery_type', '=', 'np')]
        res = self.env['delivery.carrier'].search(domain, limit=1)
        if len(res) > 0 and res.np_api_key:
            return res.np_api_key
        else:
            return None

    def _merge_two_dicts(self, x, y):
        '''Given two dicts, merge them into a new dict as a shallow copy.'''
        z = x.copy()
        z.update(y)
        return z

    @api.model
    def cron_update(self, params=None, static_ref=None, api_key=''):
        if params is None:
            params = {}
        if static_ref is None:
            static_ref = {}
        if not api_key:
            api_key = self._get_np_api_key()
        if not api_key:
            _logger.warn('Unable to update %s. No API key' % self._name)
            return False

        counter = 0
        np_api = NPApi(api_key)
        try:
            data = np_api[self._np_model][self._np_method](**params)
        except NPException, e:
            _logger.warn('Nova Poshta API exception')
            return False
        if data:
            for item in data:
                counter += 1
                vals = {}
                for k, v in self._np_mapping.iteritems():
                    vals[k] = item[v]
                rec = self.search(
                    [(self._np_key,
                      '=',
                      item[self._np_mapping[self._np_key]])], limit=1)
                vals = self._merge_two_dicts(vals, static_ref)
                if len(rec) > 0:
                    rec.write(vals)
                else:
                    self.create(vals)
        return counter


# Адреса
# Справочник городов компании
class NPCities(models.Model):
    _name = 'delivery.carrier.np.cities'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Address'
    _np_method = 'getCities'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'area': 'Area',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)
    area = fields.Char(string='Area', readonly=True,)


# Справочник географических областей Украины
class NPAreas(models.Model):
    _name = 'delivery.carrier.np.areas'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Address'
    _np_method = 'getAreas'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'areas_center': 'AreasCenter',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)
    areas_center = fields.Char(string='Area Center', readonly=True,)


# Справочник типов отделений компании
class NPWarehouseTypes(models.Model):
    _name = 'delivery.carrier.np.warehouse.types'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'AddressGeneral'
    _np_method = 'getWarehouseTypes'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)


# Справочник отделений компании
class NPWarehouses(models.Model):
    _name = 'delivery.carrier.np.warehouses'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'AddressGeneral'
    _np_method = 'getWarehouses'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'type_of_wh': 'TypeOfWarehouse',
        'wh_number': 'Number',
        'city_ref': 'CityRef',
        'city_desc': 'CityDescription',
        'max_weight': 'TotalMaxWeightAllowed',
        'place_max_weight': 'PlaceMaxWeightAllowed',
    }
    name = fields.Char(string='Description', readonly=True,)
    ref = fields.Char(string='Reference', readonly=True,)
    type_of_wh = fields.Char(string='Type Of Warehouse', readonly=True,)
    wh_number = fields.Integer(string='Number', readonly=True,)
    city_ref = fields.Char(string='City Reference', readonly=True,)
    city_desc = fields.Char(string='City Description', readonly=True,)
    max_weight = fields.Integer(
        string='Total Max Weight Allowed',
        readonly=True,)
    place_max_weight = fields.Integer(
        string='Place Max Weight Allowed',
        readonly=True,)


# Справочник улиц компании
class NPStreets(models.Model):
    _name = 'delivery.carrier.np.streets'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Address'
    _np_method = 'getStreet'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'street_type_ref': 'StreetsTypeRef',
        'street_type': 'StreetsType',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)
    street_type_ref = fields.Char(string='Street Type Reference')
    street_type = fields.Char(string='Street Type')
    city_ref = fields.Char(string='City Reference', readonly=True,)


# Контрагенты
# Справочник контрагентов
class NPCounterparties(models.Model):
    _name = 'delivery.carrier.np.counterparties'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Counterparty'
    _np_method = 'getCounterparties'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'city_ref': 'City',
        'first_name': 'FirstName',
        'middle_name': 'MiddleName',
        'last_name': 'LastName',
        'ownership_form': 'OwnershipFormRef',
        'edrpou': 'EDRPOU',
        'cp_type': 'CounterpartyType',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference')
    city_ref = fields.Char(string='City Reference')
    first_name = fields.Char(string='First Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    ownership_form = fields.Char(string='Ownership Form Ref')
    edrpou = fields.Char(string='EDRPOU')
    cp_type = fields.Char(string='Counterparty Type')
    cp_property = fields.Char(string='Counterparty Property')
    # Recipient or Sender


# Справочник контактных лиц контрагента
class NPCounterpartyContactPerson(models.Model):
    _name = 'delivery.carrier.np.cpcontactperson'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Counterparty'
    _np_method = 'getCounterpartyContactPersons'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'phone': 'Phones',
        'email': 'Email',
        'first_name': 'FirstName',
        'middle_name': 'MiddleName',
        'last_name': 'LastName',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    first_name = fields.Char(string='First Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    cp_ref = fields.Char(string='Counterparty Reference', readonly=True,)


# Справочник список адресов контрагента
class NPCounterpartyAddresses(models.Model):
    _name = 'delivery.carrier.np.cpaddress'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Counterparty'
    _np_method = 'getCounterpartyAddresses'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)
    cp_ref = fields.Char(string='Counterparty Reference', readonly=True,)


# Общий
# Формы собственности
class NPOwnershipForm(models.Model):
    _name = 'delivery.carrier.np.ownership.form'
    _inherit = 'delivery.carrier.np.model'
    _np_model = 'Common'
    _np_method = 'getOwnershipFormsList'
    _np_mapping = {
        'name': 'Description',
        'ref': 'Ref',
        'full_name': 'FullName'
    }
    name = fields.Char(string='Description')
    ref = fields.Char(string='Reference', readonly=True,)
    full_name = fields.Char(string='Full Name', readonly=True,)
