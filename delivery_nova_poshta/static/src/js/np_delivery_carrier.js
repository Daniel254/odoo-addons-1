odoo.define('np_delivery_carrier.np_delivery_carrier', function (require) {
'use strict';

var ajax = require('web.ajax');
var citiesBH = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: '/np/cities?query=%QUERY',
        wildcard: '%QUERY'
    }
});

$(document).ready(function () {
    $('input[name="city"]').typeahead(null, {
        name: 'cities',
        display: 'Description',
        source: citiesBH,
    }).on('typeahead:selected', function(evt, item) {
        $('input[name="city_ref"]').val(item.Ref);
    });
    $('input[name="street2"]').typeahead(null, {
        name: 'streets',
        display: 'Description',
        source: function function_name(query, syncResults, asyncResults) {
            var city = $('input[name="city_ref"]').val();
            ajax.jsonRpc('/np/streets', 'call', {'street': query, 'city': city})
                .then(function(data){
                    asyncResults(data);
                });
        }
    }).on('typeahead:selected', function(evt, item) {
        $('input[name="street_ref"]').val(item.Ref);
    });
});

});
