""" Launches the wavemeter monitor/control application """

from pylabnet.launchers.launcher import Launcher
from pylabnet.launchers.servers import si_tt
from pylabnet.scripts.counter import count_histogram


def main():

    launcher = Launcher(
        script=[count_histogram],
        server_req=[si_tt],
        gui_req=[None],
        params=[None],
        config='histogram'
    )
    launcher.launch()


if __name__ == '__main__':
    main()
