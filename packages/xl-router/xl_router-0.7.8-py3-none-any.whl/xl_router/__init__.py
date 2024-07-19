from xl_router.router import Router
from flask import Flask, request 
from flask.json import JSONEncoder
from importlib import import_module
import decimal


class JsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return JSONEncoder.default(self, obj)


class App(Flask):
    resources = []

    def __init__(self, config, *args, **kwargs):
        super().__init__('', *args, **kwargs)
        self.json_provider_class = JsonEncoder
        self.json.ensure_ascii = False
        if isinstance(config, dict):
            self.config.from_mapping(config)
        elif '.py' in config:
            self.config.from_pyfile(config)

    def register_extensions(self):
        pass

    def register_resources(self):
           for module_name in self.resources:
               module = import_module('app.core.{}.resources'.format(module_name))
               self.register_blueprint(module.router)

def get_user_agent():
    return request.user_agent.string.lower()


def get_ip():
    nodes = request.headers.getlist("X-Forwarded-For")
    return nodes[0] if nodes else request.remote_addr


def get_rule():
    return request.url_rule


def get_platform():
    user_agent = get_user_agent()
    if 'windows' in user_agent:
        return 1
    if 'mac os' in user_agent and 'iphone' not in user_agent:
        return 1
    return 2