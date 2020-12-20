from pylabnet.utils.helper_methods import load_device_config
from pylabnet.network.core.service_base import ServiceBase
from pylabnet.network.core.generic_server import GenericServer

import socket
import os


class Dummy:
    pass


def launch(**kwargs):
    """ Launches a dummy hardware driver and instantiates server """

    log = kwargs['logger']
    log.info(f'Launching with config {kwargs["config"]}')
    config = load_device_config(os.path.basename(__file__)[:-3], kwargs['config'], log)

    dum = Dummy()
    dum_service = ServiceBase()
    dum_service.assign_module(module=dum)
    dum_service.assign_logger(logger=log)
    dum_server = GenericServer(
        service=dum_service,
        host=socket.gethostbyname_ex(socket.gethostname())[2][0],
        port=kwargs['port']
    )
    dum_server.start()
