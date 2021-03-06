from pyvisa import ResourceManager, VisaIOError
import socket
from pylabnet.hardware.awg.dio_breakout import Driver
from pylabnet.utils.helper_methods import get_ip, show_console, hide_console, load_device_config
from pylabnet.network.client_server.dio_breakout import Service, Client
from pylabnet.network.core.generic_server import GenericServer


def launch(**kwargs):
    """ Connects to DIO breakout and instantiates server

    :param kwargs: (dict) containing relevant kwargs
        :logger: instance of LogClient for logging purposes
        :port: (int) port number for the DIO breakout server
        :config: (str) name of config file to us
    """

    device_config = load_device_config('dio_breakout', kwargs['config'], logger=kwargs['logger'])

    # Try to load settings
    if 'resource_name' in device_config:
        addr = device_config['resource_name']
    else:
        addr = device_config['device_id']

    # Try to connect
    try:
        dio = Driver(address=addr, logger=kwargs['logger'])

    # If it fails, prompt the user to enter GPIB address from resource list
    except VisaIOError:
        rm = ResourceManager()
        rs = rm.list_resources()
        rs_list = '------------------------\nAvailable resources:\n'
        for index, resource in enumerate(rs):
            rs_list += f'{index}: {resource}\n'
        rs_list+='------------------------\n'
        show_console()
        print(rs_list)
        address_index = int(input('Enter the index of the desired resource: '))
        hide_console()
        dio = Driver(address=rs[address_index], logger=kwargs['logger'])

    # Instantiate Service and server
    dio_service = Service()
    dio_service.assign_module(module=dio)
    dio_service.assign_logger(logger=kwargs['logger'])
    dio_server = GenericServer(
        service=dio_service,
        host=get_ip(),
        port=kwargs['port']
    )
    dio_server.start()
