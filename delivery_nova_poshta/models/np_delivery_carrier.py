# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.exceptions import UserError
from openerp.tools import ustr
from datetime import datetime
import logging
from npapi2 import NPApi, NPException

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    np_document_url = fields.Char(string=u"Експрес-Накладна")
    np_description = fields.Char(string=u'Опис відправлення')

    @api.model
    def create(self, vals):
        if 'carrier_id' in vals:
            domain = [('delivery_type', '=', 'np')]
            np_id = self.env['delivery.carrier'].search(
                domain, limit=1)
            if vals['carrier_id'] == np_id.id:
                vals.update({
                    'np_description': np_id.default_description or u'Товар'
                })
        return super(StockPicking, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'carrier_id' in vals:
            domain = [('delivery_type', '=', 'np')]
            np_id = self.env['delivery.carrier'].search(
                domain, limit=1)
            if vals['carrier_id'] == np_id.id:
                vals.update({
                    'np_description': np_id.default_description or u'Товар'
                })
        return super(StockPicking, self).write(vals)


class NpDeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('np', u'Нова Пошта')])

    np_api_key = fields.Char(string='Api Key')
    default_description = fields.Char(
        string=u'Типовий опис відправлення',
        default=u'Товар')

    @api.onchange('np_api_key')
    def onchange_np_api_key(self):
        np_models = (
            'delivery.carrier.np.cities',
            'delivery.carrier.np.areas',
            'delivery.carrier.np.warehouse.types',
            'delivery.carrier.np.warehouses',
            'delivery.carrier.np.ownership.form'
        )
        if self.delivery_type != 'np':
            return
        for np_obj in np_models:
            res = self.env[np_obj].cron_update(api_key=self.np_api_key)
            if not res:
                self.np_api_key = ''
                raise UserError("Невірний ключ АРІ")
                break

    def _get_weight_volume(self, order=None, picking=None):
        weight = 0.0
        volume = 0.0
        cost = 0.0
        items = order.order_line if order is not None else picking.move_lines
        for line in items:
            if line.product_uom_qty <= 0:
                continue
            if order is not None:
                if order.carrier_id.product_id.id == line.product_id.id:
                    continue
            if picking is not None:
                if picking.carrier_id.product_id.id == line.product_id.id:
                    continue
            defalut_uom_id = line.product_id.uom_id
            so_uom_id = line.product_uom
            so_qty = line.product_uom_qty
            default_uom_qty = self.env['product.uom']._compute_qty(
                so_uom_id.id,
                so_qty,
                defalut_uom_id.id)
            weight += default_uom_qty * line.product_id.weight
            volume += default_uom_qty * line.product_id.volume
            price = line.product_id.list_price
            uah_id = self.env['res.currency'].search(
                [('name', '=', 'UAH')], limit=1)
            if uah_id and uah_id.id != line.product_id.currency_id.id:
                price = line.product_id.currency_id.compute(
                    line.product_id.list_price,
                    uah_id, round=False)
            cost += default_uom_qty * price
        weight = weight if weight > 0.0 else 0.1
        volume = volume if volume > 0.0 else 0.0004
        cost = cost if cost > 0.0 else 300.0
        return weight, volume, cost

    def np_get_shipping_price_from_so(self, orders):
        prices = []
        for order in orders:
            recipient = order.partner_shipping_id
            sender = order.warehouse_id.partner_id
            if not recipient.is_nova_poshta_addr or \
                    not sender.is_nova_poshta_addr:
                prices.append(0.00)
                _logger.warn('Shipping address is not for Nova Poshta')
                continue
            service_type = sender.np_service_type + recipient.np_service_type
            api_key = self.env['delivery.carrier.np.model']._get_np_api_key()
            try:
                if not api_key:
                    _logger.warn('No API key')
                    raise UserError(u'Не вказано ключ API Нової Пошти')
                    prices.append(0.00)
                    continue
                weight, volume, cost = self._get_weight_volume(order=order)
                np_api = NPApi(api_key)
                shipping_date = fields.Date.from_string(order.date_order)
                today = fields.Date.from_string(
                    fields.Date.today())
                if shipping_date < today:
                    np_date = today
                else:
                    np_date = shipping_date
                data = np_api.InternetDocument.getDocumentPrice(
                    DateTime=np_date.strftime('%d.%m.%Y'),

                    Sender=sender._get_cp_ref(),
                    CitySender=sender.np_city_ref,
                    SenderAddress=sender._get_cp_address(),
                    ContactSender=sender._get_cp_contact(),
                    SendersPhone=sender.np_phone,

                    Recipient=recipient._get_cp_ref(),
                    CityRecipient=recipient.np_city_ref,
                    RecipientAddress=recipient._get_cp_address(),
                    ContactRecipient=recipient._get_cp_contact(),
                    RecipientsPhone=recipient.np_phone,

                    Weight=weight,
                    VolumeGeneral=volume,
                    Cost=order.amount_total,
                    ServiceType=service_type,
                    PaymentMethod=sender.np_payment_type,
                    PayerType=sender.np_payer_type,
                    CargoType=sender.np_cargo_type,)
                if data and data[0]['Cost']:
                    prices.append(data[0]['Cost'])
                else:
                    prices.append(0.00)
            except NPException, e:
                prices.append(0.00)
                _logger.warn('Nova Poshta API exception')
                raise UserError(e.msg)

        return prices

    def np_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            recipient = picking.partner_id
            sender = picking.picking_type_id.warehouse_id.partner_id
            if not recipient.is_nova_poshta_addr or \
                    not sender.is_nova_poshta_addr:
                res.append(
                    {'exact_price': 0.00,
                     'tracking_number': ''})
                _logger.warn('Shipping address is not for Nova Poshta')
                continue
            service_type = sender.np_service_type + recipient.np_service_type
            api_key = self.env['delivery.carrier.np.model']._get_np_api_key()
            try:
                if not api_key:
                    _logger.warn('No API key')
                    raise UserError(u'Не вказано ключ API Нової Пошти')
                    res.append(
                        {'exact_price': 0.00,
                         'tracking_number': ''})
                    continue
                weight, volume, cost = self._get_weight_volume(picking=picking)
                np_api = NPApi(api_key)
                shipping_date = fields.Date.from_string(picking.min_date)
                today = fields.Date.from_string(
                    fields.Date.today())
                if not shipping_date or shipping_date < today:
                    np_date = today
                else:
                    np_date = shipping_date
                data = np_api.InternetDocument.save(
                    DateTime=np_date.strftime('%d.%m.%Y'),

                    Sender=sender._get_cp_ref(),
                    CitySender=sender.np_city_ref,
                    SenderAddress=sender._get_cp_address(),
                    ContactSender=sender._get_cp_contact(),
                    SendersPhone=sender.np_phone,

                    Recipient=recipient._get_cp_ref(),
                    CityRecipient=recipient.np_city_ref,
                    RecipientAddress=recipient._get_cp_address(),
                    ContactRecipient=recipient._get_cp_contact(),
                    RecipientsPhone=recipient.np_phone,

                    Weight=weight,
                    VolumeGeneral=volume,
                    Cost=cost,
                    ServiceType=service_type,
                    PaymentMethod=sender.np_payment_type,
                    PayerType=sender.np_payer_type,
                    CargoType=sender.np_cargo_type,
                    SeatsAmount='1',
                    Description=picking.np_description)
                if data:
                    docn = data[0]['IntDocNumber']
                    attachment_url = 'https://my.novaposhta.ua/'
                    attachment_url += 'orders/printDocument/orders[]/'
                    attachment_url += docn
                    attachment_url += '/type/pdf/apiKey/'
                    attachment_url += api_key
                    picking.np_document_url = attachment_url
                    res.append({
                        'exact_price': data[0]['CostOnSite'],
                        'tracking_number': docn,
                    })
            except NPException, e:
                res.append(
                    {'exact_price': 0.00,
                     'tracking_number': ''})
                _logger.warn('Nova Poshta API exception')
                raise UserError(e.msg)
        return res

    def np_get_tracking_link(self, pickings):
        np_tracking = 'https://novaposhta.ua/tracking/?cargo_number='
        links = []
        for p in pickings:
            links.append(np_tracking + p.tracking_number)
        return links

    def np_cancel_shipment(self, pickings):
        pass
        return
