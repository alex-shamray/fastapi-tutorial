from nameko.standalone.rpc import ServiceRpcProxy

from app.core.config import settings


def rpc_proxy():
    config = {
        'AMQP_URI': settings.AMQP_URI  # e.g. "pyamqp://guest:guest@localhost"
    }
    return ServiceRpcProxy("tasks", config)
