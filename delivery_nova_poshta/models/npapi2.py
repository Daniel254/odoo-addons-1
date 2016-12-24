# -*- coding: utf-8 -*-

import requests

import logging
from logging import NullHandler

# Simple NovaPoshta RPC-style API wrapper
#
# How to use
# ==========
#
# Create instance of NPApi class for your API Key::
#
#     >>> api = NPApi('my auth key')
#
# Access any Nova Poshta model and call any Nova Poshta
# method in one of following ways::
#
#     >>> api['<model>']['<method>']({<args>})
#     >>> api['<model>']['<method>'](Parametr1=42, Parametr3='String data')
#     >>> api.model.method({<args>})
#     >>> api.model.method(Parametr1=42, Parametr3='String data')
#
# For example::
#
#     >>> cities = api.Address.getCities()
#     >>> kyiv = api.Address.getCities(FindByString='Київ')
#     >>> print(kyiv)
#     [{u'Area': u'71508131-9b87-11de-822f-000c2965ae0e',
#       u'CityID': u'4',
#       u'Conglomerates': [u'd4771ed0-4fb7-11e4-91b8-2f592fe1dcac',
#       u'f86b75e9-42f4-11e4-91b8-2f592fe1dcac'],
#       u'Delivery1': u'1',
#       u'Delivery2': u'1',
#       u'Delivery3': u'1',
#       u'Delivery4': u'1',
#       u'Delivery5': u'1',
#       u'Delivery6': u'1',
#       u'Delivery7': u'0',
#       u'Description': u'\u041a\u0438\u0457\u0432',
#       u'DescriptionRu': u'\u041a\u0438\u0435\u0432',
#       u'Ref': u'8d5a980d-391c-11dd-90d9-001a92567626'}]
#
# Or call same method, without implicit response processing,
# in this case you can manualy process errors, info, success
# and warnings sections::
#
#     >>> kyiv_res = api.Address.getCities.call(FindByString='Київ')
#     >>> print(kyiv_res)
#     {u'data': [{u'Area': u'71508131-9b87-11de-822f-000c2965ae0e',
#        u'CityID': u'4',
#        u'Conglomerates': [u'd4771ed0-4fb7-11e4-91b8-2f592fe1dcac',
#         u'f86b75e9-42f4-11e4-91b8-2f592fe1dcac'],
#        u'Delivery1': u'1',
#        u'Delivery2': u'1',
#        u'Delivery3': u'1',
#        u'Delivery4': u'1',
#        u'Delivery5': u'1',
#        u'Delivery6': u'1',
#        u'Delivery7': u'0',
#        u'Description': u'\u041a\u0438\u0457\u0432',
#        u'DescriptionRu': u'\u041a\u0438\u0435\u0432',
#        u'Ref': u'8d5a980d-391c-11dd-90d9-001a92567626'}],
#     u'errors': [],
#     u'info': [],
#     u'success': True,
#     u'warnings': []}


__author__ = "Dmytro Katyukha <firemage.dima@gmail.com>"
__version__ = "0.0.1"


_logger = logging.getLogger(__name__)
_logger.addHandler(NullHandler())


__all__ = ('NPApi', 'NPException')


class NPException(Exception):
    """ Nova Poshta exception
    """
    def __init__(self, msg, response_data=None):
        self.msg = msg
        self._response_data = response_data
        super(NPException, self).__init__(msg)

    @property
    def reponse_data(self):
        """ Full json-decoded response data, including
            errors, warnings, etc sections.
        """
        return self._response_data


class NPApi(object):
    """ Nova Poshta API class
    """
    def __init__(self, api_key, url='https://api.novaposhta.ua/v2.0/json/'):
        self._api_key = api_key
        self._url = url
        self._models = {}

    @property
    def api_key(self):
        """ API Key used by this instance
        """
        return self._api_key

    @property
    def url(self):
        """ NovaPoshta API URL
        """
        return self._url

    def get_model(self, name):
        """ Get Nova Poshta model
        """
        model = self._models.get(name, None)
        if model is None:
            model = NPModel(self, name)
            self._models[name] = model
        return model

    def __getattr__(self, name):
        return self.get_model(name)

    def __getitem__(self, name):
        return self.get_model(name)


class NPModel(object):
    """ Nova Poshta model abstraction layer

        instances of this class should be created
        implicitly via NPApi instances
    """
    def __init__(self, api, name):
        self._api = api
        self._name = name
        self._methods = {}

    @property
    def name(self):
        """Model name
        """
        return self._name

    @property
    def api(self):
        """ NPApi instalce this model belongs to
        """
        return self._api

    def get_method(self, method_name):
        """ Get model method instance
        """
        method = self._methods.get(method_name, None)
        if method is None:
            method = NPMethod(self, method_name)
            self._methods[method_name] = method
        return method

    def __getattr__(self, name):
        return self.get_method(name)

    def __getitem__(self, name):
        return self.get_method(name)


class NPMethod(object):
    """ Nova Poshta method abstration layer

        This simple class wraps Nova Poshta method calls,
        make the look simpler. Also it provides basic response processing,
        automatically logging, info, warnings, and raising exceptions
        if errors found.

        There are two posible ways to call method:
        1. use ``api.Model.Method.call(<args>)``.
           in this case no rsponse processing will be done.
        2. use ``api.Model.Method(<args>)``.
           in this case reposnse will be automatically processed
           including checks for errors, warnings, info, and success status
    """
    def __init__(self, model, name):
        self._model = model
        self._name = name

    @property
    def name(self):
        """ Method name
        """
        return self._name

    @property
    def model(self):
        """ Model this method belongs to
        """
        return self._model

    @property
    def api(self):
        """ NPApi instance this method belongs to
        """
        return self.model.api

    def _prepare_method_data(self, *args, **kwargs):
        """ Process arguments and keyword arguments to discaver call type
            if only one argument passed, then it should be dict
            with method parametrs else keyword arguments
            are treated as method parametrs
        """
        if args:
            assert len(args) == 1, "Expected max one positional argument"
            assert isinstance(args[0], dict), (
                "First positional argument expectedto be dict")
            data = args[0]
        else:
            data = kwargs

        return {
            "calledMethod": self.name,
            "methodProperties": data,
            "modelName": self.model.name,
            "apiKey": self.api.api_key,
        }

    def _process_result(self, result):
        """ Process call result

            Check for info, errors, warnings, etc.
            Info and warnings will be just logged.
            If there were errors present, then NPException will be raised
            Also of result['success'] is False,
            then NPException will be raised too

            Returns result['data']
        """
        if result['errors']:
            msg = u"Nova Poshta error: '%s'"
            msg = msg % ", ".join((str(e) for e in result['errors']))
            _logger.error(msg, exc_info=True)
            raise NPException(msg, result)
        if result['warnings']:
            msg = u"Nova Poshta warning: '%s'"
            msg = msg % ", ".join((str(e) for e in result['warnings']))
            _logger.warn(msg)
        if result['info']:
            msg = u"Nova Poshta info: '%s'"
            msg = msg % ", ".join((str(e) for e in result['warnings']))
            _logger.info(msg)

        if not result['success']:
            _logger.error("Non successful response", exc_info=True)
            raise NPException("Nova Poshta API: Not successful response",
                              result)

        return result['data']

    def call(self, *args, **kwargs):
        """ Call method (without processing result),
            differs from __call__ in case,
            this code does not process result
            Reutrns unmodified json-decoded response
        """
        method_data = self._prepare_method_data(*args, **kwargs)
        res = requests.post(self.api.url, json=method_data)
        res.raise_for_status()  # raise error if status not OK
        return res.json()

    def __call__(self, *args, **kwargs):
        """ Call method, and process result

            returns only 'data' section of response
        """
        result = self.call(*args, **kwargs)
        return self._process_result(result)
