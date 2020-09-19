from pylabnet.network.client_server import toptica_dl_pro, external_gui
from pylabnet.scripts.lasers import wlm_monitor
from pylabnet.utils.logging.logger import LogHandler
from pylabnet.utils.helper_methods import unpack_launcher, get_gui_widgets
from pylabnet.gui.pyqt.external_gui import Window

import socket
import time


class Controller:
    """ Class for controlling Toptica scan and laser properties """

    def __init__(self, dlc: toptica_dl_pro.Client,
        gui='toptica_control', logger=None, port=None):
        """ Initializes toptica specific parameters

        :param dlc: DLC client for the Toptica laser
        :param gui: .ui file to use
        :param logger: LogClient for logging purposes
        :param port: port number of script server
        """

        self.log = LogHandler(logger)

        # Setup GUI
        self.gui = Window(
            gui_template=gui,
            host=socket.gethostbyname(socket.gethostname()),
            port=port
        )
        self.widgets = get_gui_widgets(
            gui=self.gui,
            on_off=1,
            temperature=1,
            temperature_actual=1,
            current=1,
            current_actual=1,
            offset=1,
            amplitude=1,
            frequency=1,
            scan=1,
            update_temp=1,
            update_current=1
        )

        self.dlc = dlc
        self.offset = 65
        self.amplitude = 100
        self.scan = False
        self.emission = False

        self._setup_GUI()

    def run(self, check_vals=False):
        """ Runs an iteration of checks for updates and implements

        :param check_vals: (bool) whether or not to check the values of current and temp
        """

        # Update actual current and temperature
        # self.gui.activate_scalar('temperature_actual')
        # self.gui.set_scalar(self.dlc.temp_act(), 'temperature_actual')
        # self.gui.deactivate_scalar('temperature_actual')

        # self.gui.activate_scalar('current_actual')
        # self.gui.set_scalar(self.dlc.current_act(), 'current_actual')
        # self.gui.deactivate_scalar('current_actual')


        # Check for on/off updates
        if self.widgets['on_off'].isChecked() != self.emission:

            # If laser was already on, turn off
            if self.emission:
                self.dlc.turn_off()
                self.emission = False
                self.log.info('Toptica DL turned off')

            # Otherwise turn on
            else:
                self.dlc.turn_on()
                self.emission = True
                self.log.info('Toptica DL turned on')

        # Now handle a scan event
        if self.widgets['scan'].isChecked() != self.scan:

            # If we were previously scanning, terminate the scan
            if self.scan:
                self.dlc.stop_scan()
                self.scan = False
                self.log.info(f'Toptica DL scan stopped')

            # Otherwise, configure and start the scan
            else:
                offset = self.widgets['offset'].value()
                amplitude = self.widgets['amplitude'].value()
                frequency = self.widgets['frequency'].value()
                self.dlc.configure_scan(
                    offset=offset,
                    amplitude=amplitude,
                    frequency=frequency
                )
                self.dlc.start_scan()
                self.scan = True
                self.log.info('Toptica DL Scan initiated '
                              f'with offset: {offset}, '
                              f'amplitude: {amplitude}, '
                              f'frequency: {frequency}')

        # Handle value checking
        if check_vals:
            self.widgets['temperature_actual'].setValue(
                self.dlc.temp_act()
            )
            self.widgets['current_actual'].setValue(
                self.dlc.current_act()
            )

        self.gui.force_update()

    def _setup_GUI(self):
        """ Sets values to current parameters """

        # Check if laser is on and update
        self.emission = self.dlc.is_laser_on()
        self.widgets['on_off'].setChecked(self.emission)

        # Get temperature setpoint and actual temperature
        self.widgets['temperature'].setValue(self.dlc.temp_sp())
        self.widgets['temperature_actual'].setValue(self.dlc.temp_act())

        # Get current setpoint and actual current
        self.widgets['current'].setValue(self.dlc.current_sp())
        self.widgets['current_actual'].setValue(self.dlc.current_act())

        # Assign button pressing
        self.widgets['update_temp'].clicked.connect(self._set_temperature)
        self.widgets['update_current'].clicked.connect(self._set_current)

    def _set_temperature(self):
        """ Sets the temperature to the setpoint value in the GUI """

        temperature = self.widgets['temperature'].value()
        self.dlc.set_temp(temperature)
        self.log.info(f'Set Toptica temperature setpoint to {temperature}')

    def _set_current(self):
        """ Sets the current to the setpoint value in the GUI """

        current = self.widgets['current'].value()
        self.dlc.set_current(current)
        self.log.info(f'Set Toptica current setpoint to {current}')


def launch(**kwargs):

    logger, loghost, logport, clients, guis, params = unpack_launcher(**kwargs)

    dlc_client = clients['toptica_dlc_pro']

    # Instantiate Monitor script
    toptica_controller = Controller(dlc_client, logger=logger, port=kwargs['server_port'])

    # Run continuously
    # Note that the actual operation inside run() can be paused using the update server
    start_time = time.time()
    check_interval = 1
    while True:

        if time.time()-start_time < check_interval:
            toptica_controller.run()
        else:
            toptica_controller.run(check_vals=True)
            start_time = time.time()
