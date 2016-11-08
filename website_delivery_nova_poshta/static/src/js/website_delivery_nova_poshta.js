odoo.define('website_delivery_nova_poshta.website_delivery_nova_poshta', function (require) {
"use strict";

var ajax = require('web.ajax');

$(document).ready(function () {
    var $is_np_addr = $("input[name='is_nova_poshta_addr']");
    var $np_service_type = $("select[name='np_service_type']");
    var $np_countpart_id = $("input[name='np_countpart_id']");

    var $np_city_name = $("input[name='np_city_name']");
    var $np_city_ref = $("input[name='np_city_ref']");
    var $np_city_id = $("input[name='np_city_id']");

    var $np_wh_name = $("input[name='np_wh_name']");
    var $np_wh_ref = $("input[name='np_wh_ref']");
    var $np_wh_id = $("input[name='np_wh_id']");

    var $np_street_name = $("input[name='np_street_name']");
    var $np_street_ref = $("input[name='np_street_ref']");
    var $np_street_id = $("input[name='np_street_id']");

    $np_city_name.autocomplete({
        source: function(request, response) {
            var domain = [['name', '=ilike', request.term + "%"]];
            ajax.jsonRpc('/np/call_kw', 'call', {
            model: 'delivery.carrier.np.cities',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: domain,
                limit: 5,
                fields: ['name', 'ref'],
                order: 'name',
            }
        }).then(function(records) {
            this.records = records;
            var suggestions = [];
            _.each(records, function(record) {
                suggestions.push({
                    data:{id: record.id, ref: record.ref},
                    value: record.name
                });
            });
            response(suggestions);
        });
        },
        select: function(event, ui) {
            $np_city_id.val(ui.item.data.id);
            $np_city_ref.val(ui.item.data.ref);
            $np_street_name.val('');
            $np_street_id.val('');
            $np_wh_name.val('');
            $np_wh_id.val('');
            $np_countpart_id.val('');
            if($np_service_type.val() === "Doors") {
                // download streets for selected city
                ajax.jsonRpc('/np/call_kw', 'call', {
                    model: 'res.partner',
                    method: 'download_np_streets',
                    args: [],
                    kwargs: {city_ref: ui.item.data.ref}
                });
            }
            // download counterparies for selected city
            ajax.jsonRpc('/np/call_kw', 'call', {
                model: 'res.partner',
                method: 'download_np_counterparties',
                args: [],
                kwargs: {city_ref: ui.item.data.ref, role: 'Recipient'}
            });
            // assign default counterparty
            ajax.jsonRpc('/np/call_kw', 'call', {
                model: 'res.partner',
                method: 'get_default_cp',
                args: [],
                kwargs: {role: 'Recipient'}
            }).then(function(res) {
                $np_countpart_id.val(res);
            });
        },
    });
    $np_wh_name.autocomplete({
        source: function( request, response ) {
            var numb = request.term.match(/\d/g);
            if(numb === null){
                return;
            }
            numb = numb.join("");
            var domain = [
                ['wh_number', '=', numb],
                ['city_ref', '=', $np_city_ref.val()]
            ];
            ajax.jsonRpc('/np/call_kw', 'call', {
            model: 'delivery.carrier.np.warehouses',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: domain,
                limit: 5,
                fields: ['name'],
                order: 'name',
            }
        }).then(function (records) {
            this.records = records;
            var suggestions = [];
            _.each(records, function (record) {
                suggestions.push({
                    data: record.id,
                    value: record.name
                });
            });
            response(suggestions);
        });
        },
        select: function(event, ui) {
            $np_wh_id.val(ui.item.data);
        },
    });
    $np_street_name.autocomplete({
        source: function( request, response ) {
            var domain = [
                ['name', '=ilike', request.term + "%"],
                ['city_ref', '=', $np_city_ref.val()]
            ];
            ajax.jsonRpc('/np/call_kw', 'call', {
            model: 'delivery.carrier.np.streets',
            method: 'search_read',
            args: [],
            kwargs: {
                domain: domain,
                limit: 5,
                fields: ['name'],
                order: 'name',
            }
        }).then(function (records) {
            this.records = records;
            var suggestions = [];
            _.each(records, function (record) {
                suggestions.push({
                    data: record.id,
                    value: record.name
                });
            });
            response(suggestions);
        });
        },
        select: function(event, ui) {
            $np_street_id.val(ui.item.data);
        },
    });

    // hide np_address block if not checked
    $is_np_addr.on('change', function () {
        if($is_np_addr.is(':checked')) {
           $("#nova_poshta_address_block").show();
        } else {
           $("#nova_poshta_address_block").hide();
        }
    });
    $("label[for='is_nova_poshta_addr']").on('click', function () {
        $is_np_addr.prop("checked", !$is_np_addr.prop("checked"));
        $is_np_addr.change();
    });

    $np_service_type.on('change', function () {
        if(this.value === "Warehouse") {
            $("#np_wh").show();
            $("#np_street").hide();
            $("#np_building").hide();
            $("#np_flat").hide();
        }
        if(this.value === "Doors") {
            $("#np_street").show();
            $("#np_building").show();
            $("#np_flat").show();
            $("#np_wh").hide();
        }
    });

    $is_np_addr.change();
    $np_service_type.change();
});


});
