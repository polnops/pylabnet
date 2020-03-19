import sys
from pylabnet.utils.logging.logger import LogService
from pylabnet.core.generic_server import GenericServer

if __name__ == '__main__':
    host = str(sys.argv[1])
    port = int(sys.argv[2])

    log_service = LogService()
    log_server = GenericServer(service=log_service, host=host, port=port)
    log_server.start()

    print("Log messages will be displayed below")