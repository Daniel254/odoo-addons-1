# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.website_sale_delivery.controllers.main \
    import website_sale
import json
import logging
import re
from openerp.exceptions import Warning
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class website_sale(website_sale):

    @http.route(['/np/call_kw'], type='json', auth='public')
    def call_kw(self, model, method, args, kwargs, path=None):
        allowed_np_models = (
            'delivery.carrier.np.cities',
            'delivery.carrier.np.warehouses',
            'delivery.carrier.np.streets')
        allowed_np_methods = (
            'download_np_streets',
            'download_np_counterparties',
            'get_default_cp')
        if (model in allowed_np_models and method == 'search_read') or \
           (model == 'res.partner' and method in allowed_np_methods):
            return getattr(
                request.registry.get(model),
                method)(request.cr, request.uid, *args, **kwargs)

    def checkout_form_validate(self, data):
        error, error_message = super(
            website_sale, self).checkout_form_validate(data)
        if not data.get('is_nova_poshta_addr'):
            return error, error_message
        mandatory_np_fields = [
            "np_service_type", "np_city_id",
            "np_phone", "np_last_name", "np_first_name"]
        # Validation
        pip_pattern = u'^[а-яА-ЯіІїЇґҐєЄ’\'"-]+$'
        for field_name in mandatory_np_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        np_last_name = data.get('np_last_name')
        if np_last_name and not error.get('np_last_name'):
            if re.search(pip_pattern, np_last_name) is None:
                error['np_last_name'] = 'error'
                error_message.append(_('Заповніть прізвище українською'))
        np_first_name = data.get('np_first_name')
        if np_first_name and not error.get('np_first_name'):
            if re.search(pip_pattern, np_first_name) is None:
                error['np_first_name'] = 'error'
                error_message.append(_('Заповніть ім’я українською'))
        np_middle_name = data.get('np_middle_name')
        if np_middle_name and not error.get('np_middle_name'):
            if re.search(pip_pattern, np_middle_name) is None:
                error['np_middle_name'] = 'error'
                error_message.append(_('Заповніть по-батькові українською'))

        if data.get('np_phone') and not error.get('np_phone'):
            g = ''.join([x for x in data['np_phone'] if x.isdigit()][-9::])
            if len(g) < 9:
                error['np_phone'] = 'error'
                error_message.append(_('Номер телефону містить менше 9 цифр'))
        if data.get('np_service_type') == 'Warehouse':
            if not data.get('np_wh_id'):
                error['np_wh_id'] = 'missing'
        if data.get('np_service_type') == 'Doors':
            if not data.get('np_street_id'):
                error['np_street_id'] = 'missing'
            if not data.get('np_building'):
                error['np_building'] = 'missing'
            if not data.get('np_flat'):
                error['np_flat'] = 'missing'
        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            if len(error_message) == 0:
                error_message.append(_('Some required fields are empty.'))
        return error, error_message

    def checkout_parse(self, address_type, data, remove_prefix=False):
        query = super(
            website_sale, self).checkout_parse(
                address_type, data, remove_prefix=remove_prefix)
        if isinstance(data, dict) and address_type == 'billing':
            if not data.get('is_nova_poshta_addr'):
                return query
            query.update({
                'is_nova_poshta_addr': data.get('is_nova_poshta_addr'),
                'np_service_type': data.get('np_service_type'),
                'np_city_id': data.get('np_city_id'),
                'np_city_ref': data.get('np_city_ref'),
                'np_countpart_id': data.get('np_countpart_id'),
                'np_wh_id': data.get('np_wh_id'),
                'np_street_id': data.get('np_street_id'),
                'np_building': data.get('np_building'),
                'np_flat': data.get('np_flat'),
                'np_phone': data.get('np_phone'),
                'np_email': data.get('np_email'),
                'np_last_name': data.get('np_last_name'),
                'np_first_name': data.get('np_first_name'),
                'np_middle_name': data.get('np_middle_name'),
            })
        return query

    def checkout_values(self, data=None):
        values = super(website_sale, self).checkout_values(data)
        if data:
            values['checkout'].update({
                'is_nova_poshta_addr': data.get('is_nova_poshta_addr'),
                'np_service_type': data.get('np_service_type'),
                'np_city_id': data.get('np_city_id'),
                'np_city_name': data.get('np_city_name'),
                'np_city_ref': data.get('np_city_ref'),
                'np_countpart_id': data.get('np_countpart_id'),
                'np_wh_name': data.get('np_wh_name'),
                'np_wh_id': data.get('np_wh_id'),
                'np_street_name': data.get('np_street_name'),
                'np_street_id': data.get('np_street_id'),
                'np_building': data.get('np_building'),
                'np_flat': data.get('np_flat'),
                'np_phone': data.get('np_phone'),
                'np_email': data.get('np_email'),
                'np_last_name': data.get('np_last_name'),
                'np_first_name': data.get('np_first_name'),
                'np_middle_name': data.get('np_middle_name'),
            })
        else:
            orm_user = request.env['res.users']
            partner = orm_user.sudo().browse(request.uid).partner_id
            np_city_orm = request.env['delivery.carrier.np.cities']
            np_city_id = None
            np_city_name = ''
            np_city_ref = ''
            np_wh_id = None
            np_wh_name = ''
            np_street_id = None
            np_street_name = ''
            np_countpart_id = partner.np_countpart_id and \
                partner.np_countpart_id.id or ''
            if partner.np_city_id:
                np_city_id = partner.np_city_id.id
                np_city_name = partner.np_city_id.name
                np_city_ref = partner.np_city_id.ref
            if partner.np_wh_id:
                np_wh_id = partner.np_wh_id.id
                np_wh_name = partner.np_wh_id.name
            if partner.np_street_id:
                np_street_id = partner.np_street_id.id
                np_street_name = partner.np_street_id.name
            values['checkout'].update({
                'is_nova_poshta_addr': partner.is_nova_poshta_addr or False,
                'np_service_type': 'Warehouse',
                'np_city_id': np_city_id,
                'np_city_name': np_city_name,
                'np_city_ref': np_city_ref,
                'np_countpart_id': np_countpart_id,
                'np_wh_id': np_wh_id,
                'np_wh_name': np_wh_name,
                'np_street_id': np_street_id,
                'np_street_name': np_street_name,
                'np_flat': partner.np_flat,
                'np_phone':  partner.np_phone,
                'np_email':  partner.np_email,
                'np_last_name':  partner.np_last_name,
                'np_first_name':  partner.np_first_name,
                'np_middle_name':  partner.np_middle_name,
            })
        return values
